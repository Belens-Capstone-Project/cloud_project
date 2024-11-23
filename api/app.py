from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "API is running"
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