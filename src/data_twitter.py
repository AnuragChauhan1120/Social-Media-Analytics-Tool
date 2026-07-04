from datetime import datetime
import os
import re
from urllib.parse import urlparse

import pandas as pd
import requests


DEFAULT_XQUIK_BASE_URL = "https://xquik.com/api/v1"


def extract_tweet_id(tweet_url: str):
    parsed = urlparse(tweet_url)
    match = re.search(r"/status(?:es)?/(\d+)", parsed.path)
    if match:
        return match.group(1)
    fallback = re.search(r"\b(\d{15,20})\b", tweet_url)
    return fallback.group(1) if fallback else None


def parse_created_at(value):
    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def normalize_xquik_tweet(tweet, tweet_id):
    author = tweet.get("author", {})
    if not isinstance(author, dict):
        author = {}
    return {
        "comment_id": tweet.get("id"),
        "author": author.get("username", ""),
        "text": tweet.get("text", ""),
        "published_at": parse_created_at(
            tweet.get("createdAt") or tweet.get("created_at") or tweet.get("created")
        ),
        "like_count": tweet.get("likeCount") or tweet.get("like_count") or 0,
        "platform": "twitter",
        "post_id": tweet_id,
    }


def fetch_xquik_replies(tweet_id: str):
    api_key = os.getenv("XQUIK_API_KEY")
    if not api_key:
        return pd.DataFrame()

    base_url = os.getenv("XQUIK_BASE_URL", DEFAULT_XQUIK_BASE_URL).rstrip("/")
    response = requests.get(
        f"{base_url}/x/tweets/search",
        params={
            "q": f"conversation_id:{tweet_id} filter:replies",
            "queryType": "Latest",
            "limit": "100",
        },
        headers={"x-api-key": api_key, "xquik-api-contract": "2026-04-29"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    tweets = payload.get("tweets", [])
    if not isinstance(tweets, list):
        return pd.DataFrame()
    rows = [
        normalize_xquik_tweet(tweet, tweet_id)
        for tweet in tweets
        if isinstance(tweet, dict)
    ]
    return pd.DataFrame(rows)


def fetch_twitter_comments(tweet_url: str):
    tweet_id = extract_tweet_id(tweet_url)
    if not tweet_id:
        return pd.DataFrame()

    xquik_rows = fetch_xquik_replies(tweet_id)
    if not xquik_rows.empty:
        return xquik_rows

    api_url = f"https://api.tweetpik.com/v2/tweet/{tweet_id}/replies?count=100"

    headers = {
        "User-Agent": "Mozilla/5.0 (SocialAnalyticsTool)"
    }

    try:
        res = requests.get(api_url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
    except requests.RequestException:
        return pd.DataFrame()

    if "data" not in data:
        return pd.DataFrame()

    rows = []
    for r in data["data"]:
        try:
            rows.append({
                "comment_id": r.get("id"),
                "author": r.get("author", {}).get("username", ""),
                "text": r.get("full_text", ""),
                "published_at": datetime.fromisoformat(r.get("created_at", "").replace("Z", "+00:00")),
                "like_count": r.get("favorite_count", 0),
                "platform": "twitter",
                "post_id": tweet_id
            })
        except (TypeError, ValueError):
            continue

    return pd.DataFrame(rows)
