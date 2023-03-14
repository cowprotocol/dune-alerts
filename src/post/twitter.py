"""
Twitter Alert Client
"""
import tweepy  # type:ignore

from src.post.base import PostClient


class TwitterClient(PostClient):
    """Forwards alerts to Twitter"""

    def __init__(self, credentials: dict[str, str]) -> None:
        auth = tweepy.OAuthHandler(
            consumer_key=credentials["consumer_key"],
            consumer_secret=credentials["consumer_secret"],
        )
        auth.set_access_token(
            key=credentials["access_token"],
            secret=credentials["access_token_secret"],
        )
        self.api = tweepy.API(auth)

    def post(self, message: str) -> None:
        self.api.update_status(status=message)
