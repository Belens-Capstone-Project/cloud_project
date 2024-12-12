README - Cloud Computing Team

Steps to Develop the API

Set Up Dependencies

Install and configure necessary libraries such as Flask, Firebase Admin SDK, TensorFlow, and Google Cloud Storage.

Integrate Flask extensions like Flask-Limiter for rate limiting and Flask-CORS for Cross-Origin Resource Sharing.

Develop the Code Logic

Implement endpoints for health checks, file upload, image prediction, and nutritional data retrieval.

Enhance security with middleware for HTTP headers and rate limiting.

Add logging for error handling and debugging.

Establish Routes and Endpoints

/ for health check.

/predict for image upload and prediction.

Test the Functionality

Use Postman to validate endpoint functionality by simulating requests and responses.

Test the API's integration with Firebase Firestore and Google Cloud Storage.

Utilizing the API

Access the API

Use the provided URL endpoint.

Ensure the HTTP method matches the endpoint’s requirements (e.g., POST for predictions).

Prediction Workflow

Send a POST request to the /predict endpoint.

Attach an image file (e.g., PNG, JPG, JPEG) to the file parameter in the request body.

Receive a JSON response containing the predicted label, nutritional information, and additional metadata.

Example Request

Endpoint: https://example-api-url/predict

Method: POST

Headers: Content-Type: multipart/form-data

Body: Attach an image file.

Example Response

{
    "status": "success",
    "prediction": "Tehbotol Sosro 250ml",
    "confidence": 95.3,
    "file_url": "https://storage.googleapis.com/bucket-name/filename.jpg",
    "gizi": {
        "total_energi": 90,
        "gula": 15,
        "lemak_jenuh": 0,
        "garam": 0,
        "protein": 1,
        "grade": "B",
        "rekomendasi": "Moderate consumption recommended"
    }
}

Tools We Use

Development:

Visual Studio Code: For writing and managing code logic.

Postman: For API testing and debugging.

Google Cloud Platform:

Cloud Storage: For storing uploaded images and other resources.

Cloud Run: To host and deploy the API as a containerized service.

Firebase Firestore: For storing predictions and metadata.

Version Control:

GitHub: For repository management, collaboration, and CI/CD workflows.

API URL Endpoint

Base URL: https://image-prediction-api.example.com

Prediction Endpoint: /predict

Deployment Workflow

Containerize the Application

Use Docker to create a container image of the Flask application.

Push the container image to Google Container Registry (GCR).

Deploy to Cloud Run

Deploy the containerized application to Google Cloud Run for a scalable and serverless execution environment.

Set Up Firebase and Cloud Storage

Initialize Firebase for Firestore and authentication.

Configure a Google Cloud Storage bucket for file uploads.

CI/CD Integration

Use GitHub Actions or Cloud Build to automate the deployment process.

Security Measures

Rate Limiting: Limit requests to 100 per day and 30 per hour per user.

Content Security: Add HTTP security headers such as Strict-Transport-Security and Content-Security-Policy.

File Validation: Restrict file uploads to specific extensions and sizes.

Logging: Enable detailed logging for monitoring and debugging purposes.

Additional Notes

Nutritional Dataset: The dataset (nutrisi.csv) contains information about various beverages, including energy, sugar, saturated fat, and grades based on their nutritional values.

Model: A pre-trained TensorFlow model (best_model.keras) is used for predictions.

Bucket Name: Ensure that the correct bucket name (image_upload_prediction_belens) is configured in the application.

Contact Us

For any questions or issues, reach out to the Cloud Computing Team via the project GitHub repository or email.
