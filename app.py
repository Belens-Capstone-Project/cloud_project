from flask import Flask, request, jsonify, render_template
import os
import re
import logging
import traceback
from functools import wraps
from datetime import datetime, timedelta
from firebase_config import initialize_firebase
from firebase_admin import auth, firestore
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import pandas as pd
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model
from google.cloud import storage
import tensorflow as tf

# Enhanced Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Initialize Firebase
initialize_firebase()
db = firestore.client()

# Flask App Setup
app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

storage_client = storage.Client()  # Initialize GCS client
bucket_name = 'image_upload_prediction_belens'
bucket = storage_client.bucket(bucket_name)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Preload and cache model
model = None
def get_model():
    global model
    if model is None:
        model = tf.keras.models.load_model('best_model (5).keras')
    return model

label_map = {
        0: 'ABC Kopi Susu',
        1: 'BearBrand',
        2: 'Benecol Lychee 100ml',
        3: 'Cimory Bebas Laktosa 250ml',
        4: 'Cimory Susu Coklat Cashew',
        5: 'Cimory Yogurt Strawberry',
        6: 'Cola-Cola 390ml',
        7: 'Fanta Strawberry 390ml',
        8: 'Floridina 350ml',
        9: 'Fruit Tea Freeze 350ml',
        10: 'Garantea',
        11: 'Golda Cappucino',
        12: 'Hydro Coco Original 250ml',
        13: 'Ichitan Thai Green Tea',
        14: 'Larutan Penyegar Rasa Jambu',
        15: 'Mizone 500ml',
        16: 'NU Green Tea Yogurt',
        17: 'Nutri Boost Orange Flavour 250ml',
        18: 'Oatside Cokelat',
        19: 'Pepsi Blue Kaleng',
        20: 'Pocari Sweat 500ml',
        21: 'Sprite 390ml',
        22: 'Tebs Sparkling 330ml',
        23: 'Teh Pucuk Harum',
        24: 'Teh Kotak 200ml',
        25: 'Tehbotol Sosro 250ml',
        26: 'Ultra Milk Coklat Ultrajaya 200ml',
        27: 'Ultramilk Fullcream 250ml',
        28: 'Yakult',
        29: 'You C 1000 Orange'
}

gizi_df = pd.read_csv('nutrisi.csv')
columns_of_interest = [
    'total_energi', 'gula', 'lemak_jenuh', 'garam', 'protein', 'grade', 'rekomendasi'
]

# Enhanced Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[
        "100 per day",
        "30 per hour"
    ],
    storage_uri="memory://",
)

# Security Headers Middleware
def configure_security_headers(app):
    @app.after_request
    def add_security_headers(response):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    return app

app = configure_security_headers(app)

def upload_to_gcs(file, filename):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_file(file, content_type=file.content_type)  # Upload file to GCS
    return blob.public_url

# Health Check Endpoint
@app.route('/')
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "API is running smoothly",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/history', methods=['GET'])
def get_user_history():
    try:
        # Check if email is provided
        user_email = request.args.get('email')
        if not user_email:
            logger.error('Email is required')
            return jsonify({
                'error': 'Email required', 
                'details': 'User email must be provided'
            }), 400

        try:
            # Verify user authentication
            user = auth.get_user_by_email(user_email)  
            user_id = user.uid  
        except auth.UserNotFoundError:
            logger.error(f'User not found: {user_email}')
            return jsonify({
                'error': 'User not found', 
                'details': 'No user found with the provided email'
            }), 404
        except Exception as auth_error:
            logger.error(f'Authentication error: {auth_error}')
            return jsonify({
                'error': 'Authentication error', 
                'details': str(auth_error)
            }), 500

        # Query history based on user_id
        try:
            predictions_ref = db.collection('predictions')
            query = predictions_ref.where('user_id', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING)
            
            # Retrieve documents
            docs = query.stream()
            
            # Convert query results to list
            history = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['doc_id'] = doc.id
                history.append(doc_data)
        except Exception as query_error:
            logger.error(f'History query error: {query_error}')
            return jsonify({
                'error': 'History retrieval failed', 
                'details': str(query_error)
            }), 500

        # Successful response
        return jsonify({
            "status": "success",
            "history": history,
            "count": len(history)
        })

    except Exception as unexpected_error:
        # Catch any unexpected errors
        logger.error(f'Unexpected error in history endpoint: {unexpected_error}')
        logger.error(traceback.format_exc())  # Log full stack trace
        return jsonify({
            'error': 'Unexpected server error', 
            'details': str(unexpected_error)
        }), 500

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if file is present
        if 'file' not in request.files:
            logger.error('No file part in the request')
            return jsonify({
                'error': 'No file part', 
                'details': 'No file was uploaded in the request'
            }), 400

        file = request.files['file']

        # Check if filename is empty
        if file.filename == '':
            logger.error('No selected file')
            return jsonify({
                'error': 'No selected file', 
                'details': 'Uploaded file has an empty filename'
            }), 400

        # Check email
        user_email = request.form.get('email')
        if not user_email:
            logger.error('Email is required')
            return jsonify({
                'error': 'Email required', 
                'details': 'User email must be provided'
            }), 400

        try:
            # Verify user authentication
            user = auth.get_user_by_email(user_email)  
            user_id = user.uid  
        except auth.UserNotFoundError:
            logger.error(f'User not found: {user_email}')
            return jsonify({
                'error': 'User not found', 
                'details': 'No user found with the provided email'
            }), 404
        except Exception as auth_error:
            logger.error(f'Authentication error: {auth_error}')
            return jsonify({
                'error': 'Authentication error', 
                'details': str(auth_error)
            }), 500

        # Try to load the model
        try:
            model = get_model()
        except Exception as model_error:
            logger.error(f'Model loading error: {model_error}')
            return jsonify({
                'error': 'Model loading failed', 
                'details': str(model_error)
            }), 500

        # Upload to Google Cloud Storage
        try:
            filename = secure_filename(file.filename)
            file_url = upload_to_gcs(file, filename)
        except Exception as upload_error:
            logger.error(f'File upload error: {upload_error}')
            return jsonify({
                'error': 'File upload failed', 
                'details': str(upload_error)
            }), 500

        # Process image for prediction
        try:
            img = Image.open(file)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            img = img.resize((120, 120))  # Resize gambar untuk input model
            img_array = np.array(img) / 255.0  # Normalisasi gambar
            img_array = np.expand_dims(img_array, axis=0)
        except Exception as image_error:
            logger.error(f'Image processing error: {image_error}')
            return jsonify({
                'error': 'Image processing failed', 
                'details': str(image_error)
            }), 500

        # Make prediction
        try:
            prediction = model.predict(img_array)
            pred_class = np.argmax(prediction, axis=1)[0]
            predicted_label = label_map.get(pred_class, "Unknown")
        except Exception as prediction_error:
            logger.error(f'Prediction error: {prediction_error}')
            return jsonify({
                'error': 'Prediction failed', 
                'details': str(prediction_error)
            }), 500

        # Retrieve nutritional information
        try:
            gizi_data = gizi_df[gizi_df['nama_produk'] == predicted_label]
            if gizi_data.empty:
                logger.warning(f'No nutritional data found for {predicted_label}')
                gizi_info = {}
            else:
                gizi_info = gizi_data[columns_of_interest].iloc[0].to_dict()
        except Exception as gizi_error:
            logger.error(f'Nutritional data retrieval error: {gizi_error}')
            return jsonify({
                'error': 'Nutritional data retrieval failed', 
                'details': str(gizi_error)
            }), 500

        # Save prediction to Firestore
        try:
            prediction_data = {
                "user_id": user_id,
                "user_email": user_email,
                "prediction": predicted_label,
                "confidence": float(np.max(prediction) * 100),
                "file_url": file_url,
                "gizi": gizi_info,
                "timestamp": datetime.utcnow().isoformat()
            }
            db.collection('predictions').add(prediction_data)
        except Exception as firestore_error:
            logger.error(f'Firestore save error: {firestore_error}')
            return jsonify({
                'error': 'Failed to save prediction', 
                'details': str(firestore_error)
            }), 500

        # Successful response
        return jsonify({
            "status": "success",
            "message": "Prediction saved successfully",
            "data": prediction_data
        })

    except Exception as unexpected_error:
        # Catch any unexpected errors
        logger.error(f'Unexpected error in predict endpoint: {unexpected_error}')
        logger.error(traceback.format_exc())  # Log full stack trace
        return jsonify({
            'error': 'Unexpected server error', 
            'details': str(unexpected_error)
        }), 500

@app.route('/test_firestore', methods=['GET'])
def test_firestore():
    try:
        test_data = {
            "test_key": "test_value",
            "timestamp": datetime.utcnow().isoformat()
        }
        doc_ref = db.collection('predictions').add(test_data)
        return jsonify({"status": "success", "doc_id": doc_ref[1].id})
    except Exception as e:
        logger.error(f"Error testing Firestore: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)


