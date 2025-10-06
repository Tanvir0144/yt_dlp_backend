#!/usr/bin/env bash
set -e

echo "🚀 Starting NTUBE Backend..."

# Install yt-dlp binary if not present
if ! command -v yt-dlp >/dev/null; then
  echo "📦 Installing yt-dlp binary..."
  curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
  chmod +x /usr/local/bin/yt-dlp
else
  echo "✅ yt-dlp already installed, updating..."
  yt-dlp -U || true
fi

# Start the FastAPI app with Gunicorn + Uvicorn worker
echo "🔥 Launching FastAPI server..."
exec gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app \
  --bind 0.0.0.0:${PORT:-8080} \
  --keep-alive 5 \
  --timeout 0
