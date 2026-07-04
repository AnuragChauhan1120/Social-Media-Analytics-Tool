Social Media Analytics Tool
===========================

Streamlit and FastAPI app for fetching public comments, normalizing them into a
single DataFrame, and running sentiment, keyword, hashtag, and emotion analysis.

Supported sources:

- YouTube comments
- Reddit comments
- Twitter/X replies
- Instagram comments

Setup
-----

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a local `.env` file for optional integrations:

```bash
YOUTUBE_API_KEY=your-youtube-api-key
DB_URI=postgresql://user:password@localhost:5432/social_analytics
XQUIK_API_KEY=your-xquik-api-key
```

Run the Streamlit app:

```bash
streamlit run src/app.py
```

Twitter/X Reply Source
----------------------

When `XQUIK_API_KEY` is set, the Twitter branch fetches replies through the
Xquik tweet search API using the tweet conversation ID. Without that key, the
existing public reply lookup remains available.

The Twitter URL parser accepts normal status URLs, query strings, and raw tweet
IDs, then returns a normalized table with `comment_id`, `author`, `text`,
`published_at`, `like_count`, `platform`, and `post_id` columns.
