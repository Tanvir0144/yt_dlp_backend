import os
import time
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.responses import JSONResponse
from services.yt_dlp_service import search_videos, get_video_info, get_stream_options
from services.youtube_api import get_trending_videos
from utils.cache import cache_get, cache_set
from utils.ratelimit import rate_limit_ok, RateLimitConfig

# === Configuration ===
API_KEY = os.getenv("API_KEY", "").strip()
REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"

# Rate limit config
RL = RateLimitConfig(capacity=40, refill_rate=2.0, burst=15)

# === App Initialization ===
app = FastAPI(
    title="SnapTube-grade YT Backend",
    version="2.0",
    description="A lightweight backend using yt-dlp and FastAPI for video search and stream info."
)

# === Middlewares ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.add_middleware(GZipMiddleware, minimum_size=512)


@app.middleware("http")
async def security_and_ratelimit(request, call_next):
    if request.url.path in ("/", "/health", "/ready", "/docs", "/openapi.json"):
        return await call_next(request)

    ip = request.client.host if request.client else "unknown"
    if not rate_limit_ok(ip=ip, key=request.url.path, cfg=RL):
        return JSONResponse({"detail": "Too Many Requests"}, status_code=429)

    if REQUIRE_API_KEY and request.headers.get("x-api-key") != API_KEY:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    return await call_next(request)


# === Routes ===

@app.get("/")
def root():
    return {"ok": True, "service": "yt-dlp-backend", "ts": int(time.time())}


@app.get("/health")
def health():
    return {"status": "ok", "uptime": int(time.time())}


@app.get("/ready")
def ready():
    return {"ready": True}


@app.get("/search")
def search(q: str = Query(...)):
    key = f"search:{q}"
    cached = cache_get(key)
    if cached:
        return {"cached": True, "items": cached}
    try:
        data = search_videos(q)
        cache_set(key, data, ttl=600)
        return {"cached": False, "items": data}
    except Exception as e:
        print("❌ /search error:", e)
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/info")
def info(url: str = Query(...)):
    key = f"info:{url}"
    cached = cache_get(key)
    if cached:
        return {"cached": True, "info": cached}
    try:
        data = get_video_info(url)
        cache_set(key, data, ttl=600)
        return {"cached": False, "info": data}
    except Exception as e:
        print("❌ /info error:", e)
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/streams")
def streams(url: str = Query(...), prefer: Optional[str] = None):
    key = f"streams:{prefer or 'auto'}:{url}"
    cached = cache_get(key)
    if cached:
        return {"cached": True, "streams": cached}
    try:
        data = get_stream_options(url, prefer)
        cache_set(key, data, ttl=600)
        return {"cached": False, "streams": data}
    except Exception as e:
        print("❌ /streams error:", e)
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/trending")
def trending(region: str = Query("BD", min_length=2, max_length=2)):
    region = region.upper()
    if region not in ("BD", "IN"):
        region = "BD"
    key = f"trending:{region}"
    cached = cache_get(key)
    if cached:
        return {"cached": True, "items": cached}
    try:
        videos = get_trending_videos(region)
        cache_set(key, videos, ttl=1800)
        return {"cached": False, "items": videos}
    except Exception as e:
        print("❌ /trending error:", e)
        return JSONResponse({"error": str(e)}, status_code=500)


# === Entry point for local run ===
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
