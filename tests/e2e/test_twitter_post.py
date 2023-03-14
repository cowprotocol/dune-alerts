import os
import unittest

import dotenv
import pytest

from src.post.twitter import TwitterClient


class TestTwitterPost(unittest.TestCase):
    @pytest.mark.skip(reason="Don't want to make a post all the time.")
    def test_twitter_post(self):
        dotenv.load_dotenv()
        client = TwitterClient(
            credentials={
                "consumer_key": os.environ["CONSUMER_KEY"],
                "consumer_secret": os.environ["CONSUMER_SECRET"],
                "access_token": os.environ["ACCESS_TOKEN"],
                "access_token_secret": os.environ["ACCESS_TOKEN_SECRET"],
            }
        )
        client.post("Hi Mom!")


if __name__ == "__main__":
    unittest.main()
