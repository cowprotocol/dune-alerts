import os
import unittest
from unittest.mock import patch

import dotenv
from dune_client.client import DuneClient

from src.query_monitor.factory import load_config
from src.runner import QueryRunner
from src.slack_client import BasicSlackClient
from tests.file import filepath


class MyTestCase(unittest.TestCase):
    @patch.object(BasicSlackClient, "post")
    def test_query_runner(self, mocked_post):
        dotenv.load_dotenv()
        query = load_config(filepath("v2-test-data.yaml")).query
        dune = DuneClient(os.environ["DUNE_API_KEY"])
        slack_client = BasicSlackClient(token="Fake Token", channel="Fake Channel")
        query_runner = QueryRunner(query, dune, slack_client)
        query_runner.run_loop()
        mocked_post.assert_called_with(
            f"{query.name} - detected 1 cases. Results available at {query.result_url()}"
        )

    @patch.object(BasicSlackClient, "post")
    def test_v3_query(self, mocked_post):
        dotenv.load_dotenv()
        query = load_config(filepath("v3-left-bounded.yaml")).query
        dune = DuneClient(os.environ["DUNE_API_KEY"])
        slack_client = BasicSlackClient(token="Fake Token", channel="Fake Channel")
        query_runner = QueryRunner(query, dune, slack_client)
        query_runner.run_loop()
        mocked_post.assert_called_with(
            f"{query.name} - detected 1 cases. Results available at {query.result_url()}"
        )

    @patch.object(BasicSlackClient, "post")
    def test_v3_last_hour(self, mocked_post):
        dotenv.load_dotenv()
        query = load_config(filepath("v3-last-hour.yaml")).query
        dune = DuneClient(os.environ["DUNE_API_KEY"])
        slack_client = BasicSlackClient(token="Fake Token", channel="Fake Channel")
        query_runner = QueryRunner(query, dune, slack_client)
        query_runner.run_loop()
        mocked_post.assert_called_with(
            f"{query.name} - detected 1 cases. Results available at {query.result_url()}"
        )


if __name__ == "__main__":
    unittest.main()
