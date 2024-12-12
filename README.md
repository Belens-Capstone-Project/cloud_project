# Cloud Computing Team

## Steps to Develop the API

1. **Set Up Dependencies**
   - Install and configure necessary libraries such as Flask, Firebase Admin SDK, TensorFlow, and Google Cloud Storage.
   - Integrate Flask extensions like Flask-Limiter for rate limiting and Flask-CORS for Cross-Origin Resource Sharing.

2. **Develop the Code Logic**
   - Implement endpoints for health checks, file upload, image prediction, and nutritional data retrieval.
   - Enhance security with middleware for HTTP headers and rate limiting.
   - Add logging for error handling and debugging.

3. **Establish Routes and Endpoints**
   - `/` for health check.
   - `/predict` for image upload and prediction.

4. **Test the Functionality**
   - Use Postman to validate endpoint functionality by simulating requests and responses.
   - Test the API's integration with Firebase Firestore and Google Cloud Storage.

## Utilizing the API

1. **Access the API**
   - Use the provided URL endpoint.
   - Ensure the HTTP method matches the endpoint's requirements (e.g., POST for predictions).

2. **Prediction Workflow**
   - Send a POST request to the `/predict` endpoint.
   - Attach an image file (e.g., PNG, JPG, JPEG) to the file parameter in the request body.
   - Receive a JSON response containing the predicted label, nutritional information, and additional metadata.

## Tools We Use

1. **Development**:
   - Visual Studio Code: For writing and managing code logic.
   - Postman: For API testing and debugging.

2. **Google Cloud Platform**:
   - Cloud Storage: For storing uploaded images and other resources.
   - Cloud Run: To host and deploy the API as a containerized service.
   - Firebase Firestore: For storing predictions and metadata.

## API URL Endpoint

- Base URL: `https://ml-api-554143246116.asia-southeast2.run.app/`
- Prediction Endpoint: `/predict`

## Deployment Workflow

1. **Containerize the Application**
   - Use Docker to create a container image of the Flask application.
   - Push the container image to Google Container Registry (GCR).

2. **Deploy to Cloud Run**
   - Deploy the containerized application to Google Cloud Run for a scalable and serverless execution environment.

3. **Set Up Firebase and Cloud Storage**
   - Initialize Firebase for Firestore and authentication.
   - Configure a Google Cloud Storage bucket for file uploads.

## Contact Us

For any questions or issues, reach out to the Cloud Computing Team via the project GitHub repository or email.
