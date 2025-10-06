import os, requests

API_KEY = os.getenv("YOUTUBE_API_KEY", "")
BASE_URL = "https://www.googleapis.com/youtube/v3"

def get_trending_videos(region="BD", max_results=20):
    if not API_KEY:
        return {"error": "Missing YouTube API key"}
    url = f"{BASE_URL}/videos"
    params = {
        "part": "snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
        "key": API_KEY
    }
    r = requests.get(url, params=params)
    data = r.json()
    items = []
    for item in data.get("items", []):
        snippet = item["snippet"]
        items.append({
            "id": item["id"],
            "title": snippet["title"],
            "channelTitle": snippet["channelTitle"],
            "channelId": snippet["channelId"],
            "thumbnail": snippet["thumbnails"]["high"]["url"],
            "duration": item["contentDetails"]["duration"],
            "views": item["statistics"].get("viewCount"),
            "publishedAt": snippet["publishedAt"],
            "region": region
        })
    return items
