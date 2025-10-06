#!/usr/bin/env bash
set -e

echo "🚀 Starting Google Cloud Run deployment..."

# === Load environment variables from .env file ===
if [ -f ".env" ]; then
  echo "📦 Loading .env file..."
  export $(grep -v '^#' .env | xargs)
else
  echo "❌ .env file not found!"
  exit 1
fi

# === Basic project info ===
SERVICE_NAME="yt-dlp-backend"
REGION="asia-southeast1"
PROJECT_ID="ntubeapp"

echo "🔧 Project: $SERVICE_NAME"
echo "🌍 Region: $REGION"

# === Deploy command ===
gcloud run deploy $SERVICE_NAME \
  --project $PROJECT_ID \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --cpu 1 \
  --memory 512Mi \
  --concurrency 10 \
  --min-instances 1 \
  --max-instances 10 \
  --no-cpu-throttling \
  --update-env-vars="REQUIRE_API_KEY=${REQUIRE_API_KEY:-false},API_KEY=${API_KEY:-},UPSTASH_REDIS_REST_URL=${UPSTASH_REDIS_REST_URL:-},UPSTASH_REDIS_REST_TOKEN=${UPSTASH_REDIS_REST_TOKEN:-},YOUTUBE_API_KEY=${YOUTUBE_API_KEY:-},YTDLP_USE_BINARY_FALLBACK=${YTDLP_USE_BINARY_FALLBACK:-true}"

echo "✅ Deployment complete!"
echo "🌐 Checking service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --project $PROJECT_ID --format='value(status.url)')
echo "🌍 Service Live at: $SERVICE_URL"

