#!/bin/bash
# ==============================================================================
# OpenAlex Dashboard - Cloud Run Deployment Script
# ==============================================================================
# This script builds and deploys the OpenAlex Dashboard to Google Cloud Run
# ==============================================================================

# Exit immediately if a command exits with a non-zero status
set -e

# ==============================================================================
# Configuration Variables
# ==============================================================================
PROJECT_ID="openalex-dashboard"
REGION="us-central1"
SERVICE_NAME="openalex-dashboard"
IMAGE_NAME="openalex-dashboard"

# ==============================================================================
# Helper Functions
# ==============================================================================
echo_step() {
    echo ""
    echo "=============================================="
    echo "$1"
    echo "=============================================="
}

echo_success() {
    echo ""
    echo "[SUCCESS] $1"
}

echo_error() {
    echo ""
    echo "[ERROR] $1" >&2
}

# ==============================================================================
# Pre-flight Checks
# ==============================================================================
echo_step "Step 1: Checking gcloud authentication"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo_error "gcloud CLI is not installed. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo_error "You are not authenticated with gcloud."
    echo "Please run: gcloud auth login"
    exit 1
fi

echo_success "gcloud is authenticated"

# Set the project
echo ""
echo "Setting project to: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# ==============================================================================
# Build Docker Image using Cloud Build
# ==============================================================================
echo_step "Step 2: Building Docker image with Cloud Build"

echo "Building image: gcr.io/$PROJECT_ID/$IMAGE_NAME"
echo ""

gcloud builds submit --tag "gcr.io/$PROJECT_ID/$IMAGE_NAME"

echo_success "Docker image built successfully"

# ==============================================================================
# Deploy to Cloud Run
# ==============================================================================
echo_step "Step 3: Deploying to Cloud Run"

# Check if Supabase secrets exist
echo "Checking Supabase secrets..."
for SECRET in SUPABASE_URL SUPABASE_ANON_KEY; do
    if ! gcloud secrets describe "$SECRET" &>/dev/null 2>&1; then
        echo_error "Secret $SECRET not found. Create it with:"
        echo "  gcloud secrets create $SECRET --data-file=-"
        exit 1
    fi
done
echo_success "Supabase secrets found"

echo "Deploying service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

gcloud run deploy "$SERVICE_NAME" \
    --image "gcr.io/$PROJECT_ID/$IMAGE_NAME" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --set-secrets "SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_ANON_KEY=SUPABASE_ANON_KEY:latest"

echo_success "Deployment completed successfully"

# ==============================================================================
# Get and Display Service URL
# ==============================================================================
echo_step "Step 4: Retrieving service URL"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform managed \
    --region "$REGION" \
    --format "value(status.url)")

echo ""
echo "=============================================="
echo "  DEPLOYMENT SUCCESSFUL!"
echo "=============================================="
echo ""
echo "  Service Name: $SERVICE_NAME"
echo "  Region:       $REGION"
echo "  Service URL:  $SERVICE_URL"
echo ""
echo "=============================================="
