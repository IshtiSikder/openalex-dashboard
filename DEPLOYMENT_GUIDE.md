# OpenAlex Dashboard Deployment Guide

This guide covers deploying the OpenAlex Dashboard Streamlit application to Google Cloud Run.

**Project Configuration:**
- GCP Project ID: `openalex-dashboard`
- Region: `us-central1`
- Service Name: `openalex-dashboard`
- Port: `8080`

---

## 1. Prerequisites

### Required Accounts and Tools
- Google Cloud Platform account with billing enabled
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed and configured
- GitHub account (for CI/CD deployment)

### Required GCP APIs
The following APIs must be enabled:
- Cloud Run API
- Cloud Build API
- Container Registry API

### Required IAM Permissions
Your account or service account needs these roles:
- `roles/run.admin` - Deploy and manage Cloud Run services
- `roles/cloudbuild.builds.editor` - Submit builds to Cloud Build
- `roles/storage.admin` - Push images to Container Registry
- `roles/iam.serviceAccountUser` - Act as service accounts

---

## 2. First-Time Setup

### Authenticate with GCP

```bash
# Login to your Google account
gcloud auth login

# Set the project
gcloud config set project openalex-dashboard

# Verify your configuration
gcloud config list
```

### Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled | grep -E "(run|cloudbuild|containerregistry)"
```

### Set Default Region

```bash
gcloud config set run/region us-central1
```

---

## 3. Manual Deployment

### Option A: Using the deploy.sh Script

```bash
# Make the script executable (first time only)
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

### Option B: Step-by-Step gcloud Commands

```bash
# Build and deploy in a single command
gcloud run deploy openalex-dashboard \
  --source . \
  --region us-central1 \
  --platform managed \
  --port 8080 \
  --allow-unauthenticated \
  --set-env-vars="OPENALEX_EMAIL=your-email@example.com"
```

### Option C: Build and Deploy Separately

```bash
# Step 1: Build the container image with Cloud Build
gcloud builds submit --tag gcr.io/openalex-dashboard/openalex-dashboard

# Step 2: Deploy the image to Cloud Run
gcloud run deploy openalex-dashboard \
  --image gcr.io/openalex-dashboard/openalex-dashboard \
  --region us-central1 \
  --platform managed \
  --port 8080 \
  --allow-unauthenticated
```

### Setting Environment Variables

```bash
# Set environment variables during deployment
gcloud run deploy openalex-dashboard \
  --image gcr.io/openalex-dashboard/openalex-dashboard \
  --region us-central1 \
  --set-env-vars="OPENALEX_EMAIL=your-email@example.com"

# Update environment variables on an existing service
gcloud run services update openalex-dashboard \
  --region us-central1 \
  --set-env-vars="OPENALEX_EMAIL=your-email@example.com"
```

### Get the Service URL

```bash
gcloud run services describe openalex-dashboard \
  --region us-central1 \
  --format='value(status.url)'
```

---

## 4. CI/CD Deployment (GitHub Actions)

### Required GitHub Secrets

Add these secrets to your repository at **Settings > Secrets and variables > Actions**:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GCP_PROJECT_ID` | `openalex-dashboard` | Your GCP project ID |
| `GCP_SA_KEY` | (JSON key contents) | Service account key for deployment |

### Create a Service Account for GitHub Actions

```bash
# Create the service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployer" \
  --project=openalex-dashboard

# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding openalex-dashboard \
  --member="serviceAccount:github-actions@openalex-dashboard.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# Grant Cloud Build Editor role
gcloud projects add-iam-policy-binding openalex-dashboard \
  --member="serviceAccount:github-actions@openalex-dashboard.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

# Grant Storage Admin role (for Container Registry)
gcloud projects add-iam-policy-binding openalex-dashboard \
  --member="serviceAccount:github-actions@openalex-dashboard.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Grant Service Account User role
gcloud projects add-iam-policy-binding openalex-dashboard \
  --member="serviceAccount:github-actions@openalex-dashboard.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download the key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@openalex-dashboard.iam.gserviceaccount.com
```

### Add the Key to GitHub

1. Open `github-actions-key.json` and copy its entire contents
2. Go to your GitHub repository **Settings > Secrets and variables > Actions**
3. Click **New repository secret**
4. Name: `GCP_SA_KEY`
5. Value: Paste the JSON key contents
6. Click **Add secret**

**Important:** Delete the local key file after adding it to GitHub:
```bash
rm github-actions-key.json
```

### How the Workflow Triggers

The GitHub Actions workflow (`.github/workflows/deploy.yml`) triggers on:
- **Push to master branch** - Automatic deployment
- **Manual trigger** - Go to Actions tab and click "Run workflow"

---

## 5. Rollback Procedure

### List Available Revisions

```bash
# List all revisions for the service
gcloud run revisions list \
  --service openalex-dashboard \
  --region us-central1

# Get details about a specific revision
gcloud run revisions describe REVISION_NAME \
  --region us-central1
```

### Option A: Using the rollback.sh Script

```bash
# Make executable (first time only)
chmod +x rollback.sh

# Run rollback (will prompt for revision name)
./rollback.sh

# Or specify revision directly
./rollback.sh openalex-dashboard-00005-abc
```

### Option B: Manual Rollback via gcloud

```bash
# Route 100% of traffic to a specific revision
gcloud run services update-traffic openalex-dashboard \
  --region us-central1 \
  --to-revisions=REVISION_NAME=100

# Example with actual revision name
gcloud run services update-traffic openalex-dashboard \
  --region us-central1 \
  --to-revisions=openalex-dashboard-00003-xyz=100
```

### Gradual Traffic Migration (Canary Deployment)

```bash
# Split traffic between old and new revisions
gcloud run services update-traffic openalex-dashboard \
  --region us-central1 \
  --to-revisions=NEW_REVISION=10,OLD_REVISION=90

# Gradually increase traffic to new revision
gcloud run services update-traffic openalex-dashboard \
  --region us-central1 \
  --to-revisions=NEW_REVISION=50,OLD_REVISION=50

# Complete migration
gcloud run services update-traffic openalex-dashboard \
  --region us-central1 \
  --to-revisions=NEW_REVISION=100
```

---

## 6. Monitoring and Logs

### View Logs via CLI

```bash
# Stream logs in real-time
gcloud run services logs tail openalex-dashboard \
  --region us-central1

# Read recent logs (last 100 entries)
gcloud run services logs read openalex-dashboard \
  --region us-central1 \
  --limit 100

# Filter logs by severity
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=openalex-dashboard \
  AND severity>=ERROR" \
  --limit 50 \
  --format="table(timestamp,severity,textPayload)"
```

### Cloud Console Links

- **Cloud Run Dashboard:** https://console.cloud.google.com/run?project=openalex-dashboard
- **Service Details:** https://console.cloud.google.com/run/detail/us-central1/openalex-dashboard/metrics?project=openalex-dashboard
- **Logs:** https://console.cloud.google.com/run/detail/us-central1/openalex-dashboard/logs?project=openalex-dashboard
- **Cloud Build History:** https://console.cloud.google.com/cloud-build/builds?project=openalex-dashboard

### Basic Troubleshooting

**Container fails to start:**
```bash
# Check logs for startup errors
gcloud run services logs read openalex-dashboard \
  --region us-central1 \
  --limit 50

# Common causes:
# - Missing environment variables
# - Port mismatch (must be 8080)
# - Application crash on startup
```

**Build fails:**
```bash
# List recent builds
gcloud builds list --limit 5

# View build logs
gcloud builds log BUILD_ID

# Test build locally (if Docker is available)
docker build -t openalex-dashboard .
docker run -p 8080:8080 openalex-dashboard
```

**Service returns errors (5xx):**
```bash
# Check service configuration
gcloud run services describe openalex-dashboard --region us-central1

# Increase memory if needed
gcloud run services update openalex-dashboard \
  --region us-central1 \
  --memory 1Gi

# Increase CPU if needed
gcloud run services update openalex-dashboard \
  --region us-central1 \
  --cpu 2
```

---

## 7. Cost Considerations

### Cloud Run Pricing Model

Cloud Run charges for:
- **CPU:** Per vCPU-second while processing requests
- **Memory:** Per GiB-second while processing requests
- **Requests:** Per million requests

### Free Tier (Monthly)

Cloud Run includes a generous free tier:
- 180,000 vCPU-seconds
- 360,000 GiB-seconds of memory
- 2 million requests

### Estimated Costs for Low Traffic

For a dashboard with approximately 1,000 requests per day:

| Component | Estimated Monthly Cost |
|-----------|------------------------|
| Cloud Run compute | $0 - $5 (mostly free tier) |
| Container Registry storage | ~$0.026/GB/month |
| Cloud Build | Free (first 120 build-minutes/day) |
| **Total** | **$0 - $10/month** |

### Cost Optimization Tips

```bash
# Scale to zero when idle (no cost when not in use)
gcloud run services update openalex-dashboard \
  --region us-central1 \
  --min-instances 0

# Limit maximum instances to control costs
gcloud run services update openalex-dashboard \
  --region us-central1 \
  --max-instances 5

# Use minimum required memory
gcloud run services update openalex-dashboard \
  --region us-central1 \
  --memory 512Mi

# Set concurrency to handle more requests per instance
gcloud run services update openalex-dashboard \
  --region us-central1 \
  --concurrency 80
```

### Set Up Budget Alerts

1. Go to **Billing > Budgets & alerts** in Cloud Console
2. Click **Create Budget**
3. Set budget amount (e.g., $25/month)
4. Configure alert thresholds (50%, 90%, 100%)
5. Add notification email addresses

---

## Quick Reference

| Task | Command |
|------|---------|
| Deploy | `gcloud run deploy openalex-dashboard --source . --region us-central1 --port 8080 --allow-unauthenticated` |
| Get URL | `gcloud run services describe openalex-dashboard --region us-central1 --format='value(status.url)'` |
| View logs | `gcloud run services logs tail openalex-dashboard --region us-central1` |
| List revisions | `gcloud run revisions list --service openalex-dashboard --region us-central1` |
| Rollback | `gcloud run services update-traffic openalex-dashboard --region us-central1 --to-revisions=REVISION=100` |
| Update env vars | `gcloud run services update openalex-dashboard --region us-central1 --set-env-vars="KEY=value"` |
| Scale settings | `gcloud run services update openalex-dashboard --region us-central1 --min-instances 0 --max-instances 10` |
