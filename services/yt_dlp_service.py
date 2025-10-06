import os
import json
import subprocess
import shutil

# Try to find yt-dlp binary (fallback for local runs)
YTDLP_BIN = shutil.which("yt-dlp")
USE_BINARY_FALLBACK = os.getenv("YTDLP_USE_BINARY_FALLBACK", "false").lower() == "true"

def _run_cmd(cmd):
    """Run shell command safely"""
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
    return [json.loads(line) for line in res.stdout.splitlines() if line.strip()]

def search_videos(query):
    """Search YouTube videos by query"""
    try:
        import yt_dlp
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
            "skip_download": True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(f"ytsearch10:{query}", download=False)
        return [
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "url": f"https://www.youtube.com/watch?v={e.get('id')}",
                "channel": e.get("channel"),
                "duration": e.get("duration"),
                "thumbnail": (e.get("thumbnails") or [{}])[-1].get("url")
            }
            for e in data.get("entries", [])
        ]
    except Exception as ex:
        # fallback to binary only if enabled
        if USE_BINARY_FALLBACK and YTDLP_BIN:
            lines = _run_cmd([YTDLP_BIN, "-j", f"ytsearch10:{query}", "--flat-playlist", "--quiet"])
            return [
                {
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "url": f"https://www.youtube.com/watch?v={e.get('id')}",
                    "channel": e.get("uploader"),
                    "thumbnail": e.get("thumbnail")
                }
                for e in lines
            ]
        raise RuntimeError(f"Search failed: {ex}")

def get_video_info(url):
    """Fetch metadata for a specific video"""
    try:
        import yt_dlp
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as ex:
        if USE_BINARY_FALLBACK and YTDLP_BIN:
            res = subprocess.run([YTDLP_BIN, "-j", url, "--quiet"], stdout=subprocess.PIPE, text=True, timeout=15)
            return json.loads(res.stdout.strip())
        raise RuntimeError(f"Info fetch failed: {ex}")

def get_stream_options(url, prefer=None):
    """Return available video/audio streams"""
    info = get_video_info(url)
    formats = info.get("formats") or []
    best_muxed = max(
        (f for f in formats if f.get("acodec") != "none" and f.get("vcodec") != "none"),
        key=lambda f: f.get("height", 0),
        default=None
    )
    best_audio = max(
        (f for f in formats if f.get("vcodec") == "none"),
        key=lambda f: f.get("abr", 0),
        default=None
    )
    return {
        "title": info.get("title"),
        "best_muxed": best_muxed,
        "best_audio": best_audio,
    }
