import os
import requests

API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
BASE_URL = "https://www.googleapis.com/youtube/v3"


def get_trending_videos(region: str = "BD", max_results: int = 20):
    """Fetch trending YouTube videos for a specific region"""
    if not API_KEY:
        return {"error": "Missing YouTube API key"}

    url = f"{BASE_URL}/videos"
    params = {
        "part": "snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "regionCode": region.upper(),
        "maxResults": max_results,
        "key": API_KEY,
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        return {"error": f"Failed to fetch trending videos: {e}"}

    items = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})
        stats = item.get("statistics", {})

        items.append({
            "id": item.get("id"),
            "title": snippet.get("title"),
            "channelTitle": snippet.get("channelTitle"),
            "channelId": snippet.get("channelId"),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
            "duration": content.get("duration"),
            "views": stats.get("viewCount"),
            "publishedAt": snippet.get("publishedAt"),
            "region": region.upper(),
        })

    return items
