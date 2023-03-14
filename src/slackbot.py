"""
Main entry point to slackbot query monitoring
"""
import argparse
import os

import dotenv

from dune_client.client import DuneClient

from src.post.base import PostClient
from src.query_monitor.base import QueryBase
from src.query_monitor.factory import load_config
from src.runner import QueryRunner
from src.slack_client import BasicSlackClient


def run_slackbot(
    query: QueryBase,
    dune: DuneClient,
    slack_client: PostClient,
    ping_frequency: int,
) -> None:
    """
    This is the main method of the program.
    Instantiate a query runner, and execute its run_loop
    """
    query_runner = QueryRunner(query, dune, slack_client, ping_frequency)
    query_runner.run_loop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Slackbot Configuration")
    parser.add_argument(
        "--query-config",
        type=str,
        help="YAML configuration file for a QueryMonitor object",
        required=True,
    )
    args = parser.parse_args()
    dotenv.load_dotenv()
    config = load_config(args.query_config)
    run_slackbot(
        query=config.query,
        dune=DuneClient(os.environ["DUNE_API_KEY"]),
        slack_client=BasicSlackClient(
            token=os.environ["SLACK_TOKEN"], channel=config.alert_channel
        ),
        ping_frequency=config.ping_frequency,
    )
