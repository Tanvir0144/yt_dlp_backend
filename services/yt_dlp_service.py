import os, json, shutil, subprocess

YTDLP_BIN = shutil.which("yt-dlp") or "/usr/local/bin/yt-dlp"
YTDLP_USE_BIN = os.getenv("YTDLP_USE_BINARY_FALLBACK", "true").lower() == "true"

def _run_cmd(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=8)
    return [json.loads(line) for line in res.stdout.splitlines() if line.strip()]

def search_videos(query):
    try:
        import yt_dlp
        ydl_opts = {'quiet': True, 'noplaylist': True, 'skip_download': True, 'dump_single_json': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(f"ytsearch10:{query}", download=False)
        return [
            {"id": e.get("id"),
             "title": e.get("title"),
             "url": f"https://www.youtube.com/watch?v={e.get('id')}",
             "channel": e.get("channel"),
             "duration": e.get("duration"),
             "thumbnail": (e.get("thumbnails") or [{}])[-1].get("url")}
            for e in data.get("entries", [])
        ]
    except Exception:
        if YTDLP_USE_BIN:
            lines = _run_cmd([YTDLP_BIN, "-j", f"ytsearch10:{query}", "--flat-playlist", "--quiet"])
            return [
                {"id": e.get("id"),
                 "title": e.get("title"),
                 "url": f"https://www.youtube.com/watch?v={e.get('id')}",
                 "channel": e.get("uploader"),
                 "thumbnail": e.get("thumbnail")}
                for e in lines
            ]
        raise

def get_video_info(url):
    try:
        import yt_dlp
        opts = {'quiet': True, 'skip_download': True, 'dump_single_json': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception:
        if YTDLP_USE_BIN:
            res = subprocess.run([YTDLP_BIN, "-j", url, "--quiet"], stdout=subprocess.PIPE, text=True, timeout=10)
            return json.loads(res.stdout.strip())
        raise

def get_stream_options(url, prefer=None):
    info = get_video_info(url)
    formats = info.get("formats") or []
    best_muxed = max((f for f in formats if f.get("acodec") != "none" and f.get("vcodec") != "none"),
                     key=lambda f: f.get("height", 0), default=None)
    best_audio = max((f for f in formats if f.get("vcodec") == "none"), key=lambda f: f.get("abr", 0), default=None)
    return {
        "title": info.get("title"),
        "best_muxed": best_muxed,
        "best_audio": best_audio,
    }
