# Exit on error
set -e

PROJECT_ID="project-belens"
REGION="asia-southeast2"
SERVICE_NAME="ml-api"

echo "Building and deploying to project: $PROJECT_ID"

# Verify credentials file exists
if [ ! -f "api/credentials/serviceAccount.json" ]; then
    echo "Error: serviceAccount.json not found in api/credentials/"
    exit 1
fi

# Verify project configuration
echo "Verifying project configuration..."
gcloud config set project $PROJECT_ID

# Verify required APIs are enabled
echo "Checking required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create secret if not exists
echo "Setting up Secret Manager..."
if ! gcloud secrets describe firebase-credentials >/dev/null 2>&1; then
    echo "Creating Firebase credentials secret..."
    gcloud secrets create firebase-credentials \
        --replication-policy="automatic"
    
    echo "Adding secret version..."
    cat api/credentials/serviceAccount.json | gcloud secrets versions add firebase-credentials --data-file=-
fi

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
    --allow-unauthenticated \
    --set-secrets FIREBASE_CREDENTIALS=firebase-credentials:latest \
    --memory 2Gi

echo "Deployment completed successfully!"