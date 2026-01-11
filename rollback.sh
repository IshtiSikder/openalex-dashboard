#!/bin/bash
# ==============================================================================
# OpenAlex Dashboard - Cloud Run Rollback Script
# ==============================================================================
# This script rolls back the OpenAlex Dashboard to a previous Cloud Run revision
# ==============================================================================

# Exit immediately if a command exits with a non-zero status
set -e

# ==============================================================================
# Configuration Variables
# ==============================================================================
PROJECT_ID="openalex-dashboard"
REGION="us-central1"
SERVICE_NAME="openalex-dashboard"

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
echo_step "OpenAlex Dashboard - Rollback Script"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo_error "gcloud CLI is not installed. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set the project
gcloud config set project "$PROJECT_ID" --quiet

# ==============================================================================
# List Recent Revisions
# ==============================================================================
echo_step "Step 1: Fetching recent revisions"

echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Get list of revisions
REVISIONS=$(gcloud run revisions list \
    --service "$SERVICE_NAME" \
    --platform managed \
    --region "$REGION" \
    --format="table(REVISION,ACTIVE,DEPLOYED,STATUS)" \
    2>/dev/null)

if [ -z "$REVISIONS" ]; then
    echo_error "No revisions found for service: $SERVICE_NAME"
    exit 1
fi

echo "$REVISIONS"
echo ""

# ==============================================================================
# Get Target Revision
# ==============================================================================
REVISION_NAME="$1"

if [ -z "$REVISION_NAME" ]; then
    echo_step "Step 2: Select revision to rollback to"

    # Get revision names only (excluding the currently active one)
    echo "Available revisions (excluding currently active):"
    echo ""

    REVISION_LIST=$(gcloud run revisions list \
        --service "$SERVICE_NAME" \
        --platform managed \
        --region "$REGION" \
        --format="value(REVISION)" \
        2>/dev/null)

    # Display numbered list
    i=1
    declare -a REVISION_ARRAY
    while IFS= read -r rev; do
        echo "  $i) $rev"
        REVISION_ARRAY[$i]="$rev"
        ((i++))
    done <<< "$REVISION_LIST"

    echo ""
    read -p "Enter revision number or name to rollback to: " SELECTION

    # Check if input is a number
    if [[ "$SELECTION" =~ ^[0-9]+$ ]]; then
        REVISION_NAME="${REVISION_ARRAY[$SELECTION]}"
        if [ -z "$REVISION_NAME" ]; then
            echo_error "Invalid selection: $SELECTION"
            exit 1
        fi
    else
        REVISION_NAME="$SELECTION"
    fi
fi

if [ -z "$REVISION_NAME" ]; then
    echo_error "No revision specified"
    exit 1
fi

echo ""
echo "Selected revision: $REVISION_NAME"

# ==============================================================================
# Confirmation Prompt
# ==============================================================================
echo_step "Step 3: Confirm rollback"

echo "You are about to rollback to revision: $REVISION_NAME"
echo ""
echo "This will route 100% of traffic to this revision."
echo ""
read -p "Are you sure you want to proceed? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ] && [ "$CONFIRM" != "y" ]; then
    echo ""
    echo "Rollback cancelled."
    exit 0
fi

# ==============================================================================
# Perform Rollback
# ==============================================================================
echo_step "Step 4: Rolling back to revision"

echo "Updating traffic to route 100% to: $REVISION_NAME"
echo ""

gcloud run services update-traffic "$SERVICE_NAME" \
    --platform managed \
    --region "$REGION" \
    --to-revisions "$REVISION_NAME=100"

echo_success "Rollback completed successfully"

# ==============================================================================
# Verify Rollback
# ==============================================================================
echo_step "Step 5: Verifying rollback"

echo "Current traffic allocation:"
echo ""

gcloud run services describe "$SERVICE_NAME" \
    --platform managed \
    --region "$REGION" \
    --format="table(traffic.revisionName,traffic.percent)"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform managed \
    --region "$REGION" \
    --format "value(status.url)")

echo ""
echo "=============================================="
echo "  ROLLBACK SUCCESSFUL!"
echo "=============================================="
echo ""
echo "  Service Name:     $SERVICE_NAME"
echo "  Active Revision:  $REVISION_NAME"
echo "  Service URL:      $SERVICE_URL"
echo ""
echo "=============================================="
