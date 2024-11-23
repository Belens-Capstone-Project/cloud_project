PROJECT_ID="lucky-antler-442613-e9"
REGION="asia-southeast2"
SERVICE_NAME="ml-api"

echo "Building and deploying to project: $PROJECT_ID"

# Build dan push Docker image
echo "Building and pushing Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy ke Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated

echo "Deployment completed!"