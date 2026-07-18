import os
import unittest
from unittest import mock

from src import data_extraction, data_twitter


class YouTubeUrlTest(unittest.TestCase):
    def test_extracts_common_youtube_url_formats(self):
        urls = {
            "https://www.youtube.com/watch?v=abcdefghijk": "abcdefghijk",
            "https://youtu.be/abcdefghijk?t=12": "abcdefghijk",
            "https://www.youtube.com/shorts/abcdefghijk": "abcdefghijk",
            "https://www.youtube.com/embed/abcdefghijk": "abcdefghijk",
            "https://www.youtube.com/live/abcdefghijk": "abcdefghijk",
        }

        for url, expected in urls.items():
            with self.subTest(url=url):
                self.assertEqual(data_extraction.extract_video_id(url), expected)

    def test_rejects_non_youtube_urls(self):
        self.assertIsNone(data_extraction.extract_video_id("https://example.com/watch?v=abcdefghijk"))


class TwitterSourceTest(unittest.TestCase):
    def test_xquik_failure_falls_back_to_existing_reply_source(self):
        fallback_response = mock.Mock()
        fallback_response.json.return_value = {
            "data": [
                {
                    "id": "reply-1",
                    "author": {"username": "reader"},
                    "full_text": "Useful context",
                    "created_at": "2026-07-18T08:00:00Z",
                    "favorite_count": 4,
                }
            ]
        }
        fallback_response.raise_for_status.return_value = None

        with mock.patch.dict(os.environ, {"XQUIK_API_KEY": "key"}, clear=True):
            with mock.patch.object(
                data_twitter.requests,
                "get",
                side_effect=[
                    data_twitter.requests.ConnectionError("temporary"),
                    fallback_response,
                ],
            ) as get:
                result = data_twitter.fetch_twitter_comments(
                    "https://x.com/example/status/1234567890123456789"
                )

        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["comment_id"], "reply-1")
        self.assertEqual(get.call_count, 2)

    def test_xquik_request_uses_conversation_query_and_api_key(self):
        response = mock.Mock()
        response.json.return_value = {"tweets": []}
        response.raise_for_status.return_value = None

        with mock.patch.dict(os.environ, {"XQUIK_API_KEY": "key"}, clear=True):
            with mock.patch.object(data_twitter.requests, "get", return_value=response) as get:
                data_twitter.fetch_xquik_replies("1234567890123456789")

        _, kwargs = get.call_args
        self.assertEqual(
            kwargs["params"]["q"],
            "conversation_id:1234567890123456789 filter:replies",
        )
        self.assertEqual(kwargs["headers"]["x-api-key"], "key")
        self.assertEqual(kwargs["timeout"], 30)


if __name__ == "__main__":
    unittest.main()
