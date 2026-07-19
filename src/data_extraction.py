import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd
import requests
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    path_parts = [part for part in parsed.path.split("/") if part]

    if hostname in {"youtu.be", "www.youtu.be"}:
        return path_parts[0] if path_parts else None

    if hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        if len(path_parts) >= 2 and path_parts[0] in {"embed", "live", "shorts"}:
            return path_parts[1]

    return None


def get_comments(video_url, max_results=200):
    """Fetch YouTube comments into a DataFrame."""
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube video URL")

    comments = []
    next_page_token = None

    while len(comments) < max_results:
        api_url = "https://www.googleapis.com/youtube/v3/commentThreads"
        params = {
            "part": "snippet",
            "videoId": video_id,
            "key": YOUTUBE_API_KEY,
            "maxResults": 100,
            "pageToken": next_page_token,
            "textFormat": "plainText"
        }

        response = requests.get(api_url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise Exception(data["error"]["message"])

        for item in data.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "comment_id": item["id"],
                "author": snippet.get("authorDisplayName"),
                "comment": snippet.get("textDisplay"),
                "likes": snippet.get("likeCount"),
                "published_at": snippet.get("publishedAt"),
                "video_id": video_id,
                "platform": "youtube"
            })

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return pd.DataFrame(comments[:max_results])


if __name__ == "__main__":
    from src.db_utils import create_comments_table, insert_comments

    print("\nFetching comments...")
    df = get_comments("https://www.youtube.com/watch?v=McXJj7sjcZ0", max_results=200)

# Remove this OR wrap it in a test block
# df = get_comments("some_video", 100)
# if df is not None and not df.empty:
#     print(df.head())


    df = df.rename(columns={
    "comment": "text",
    "likes": "like_count"  # ✅ Ensure correct matching
})
  # ✅ FIX ADDED HERE

    create_comments_table()
    insert_comments(df)
    print("✅ Comments inserted into PostgreSQL!\n")
