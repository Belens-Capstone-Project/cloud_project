from flask import Flask, request, jsonify
import os
from .firebase_config import initialize_firebase
from firebase_admin import auth
from functools import wraps

initialize_firebase()

app = Flask(__name__)

def verify_firebase_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "No token provided"}), 401
            
        try:
            token = auth_header.split(' ')[1]  # Remove 'Bearer '
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401
            
    return decorated_function


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "API is running"
    })


@app.route('/auth-test', methods=['GET'])
@verify_firebase_token
def auth_test():
    return jsonify({
        "status": "success",
        "message": "Authenticated successfully",
        "user_id": request.user['uid']
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # Validasi input
        if not data:
            return jsonify({
                "error": "No data provided"
            }), 400
            
        image_url = data.get('image_url')
        if not image_url:
            return jsonify({
                "error": "image_url is required"
            }), 400
            
        # Placeholder response
        return jsonify({
            "status": "success",
            "prediction": {
                "class": "Placeholder Class",
                "confidence": 0.0,
                "message": "Model belum diintegrasikan"
            },
            "input_received": {
                "image_url": image_url
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)