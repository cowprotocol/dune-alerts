import os
import unittest
from unittest.mock import patch

import dotenv
from dune_client.client import DuneClient

from src.legacy_dune import LegacyDuneClient
from src.query_monitor.factory import load_from_config
from src.runner import QueryRunner
from src.slack_client import BasicSlackClient


class MyTestCase(unittest.TestCase):
    @patch.object(BasicSlackClient, "post")
    def test_query_runner(self, mocked_post):
        dotenv.load_dotenv()
        query = load_from_config("./tests/data/v2-test-data.yaml")
        dune = DuneClient(os.environ["DUNE_API_KEY"])
        slack_client = BasicSlackClient(token="Fake Token", channel="Fake Channel")
        query_runner = QueryRunner(query, dune, slack_client)
        query_runner.run_loop()
        mocked_post.assert_called_with(
            f"{query.name} - detected 1 cases. Results available at {query.result_url()}"
        )


if __name__ == "__main__":
    unittest.main()
