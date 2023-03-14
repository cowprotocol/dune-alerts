"""
Main entry point to slackbot query monitoring
"""
import argparse
import os

import dotenv

from dune_client.client import DuneClient

from src.post.base import PostClient
from src.post.twitter import TwitterClient
from src.query_monitor.base import QueryBase
from src.query_monitor.factory import load_config, AlertType
from src.runner import QueryRunner
from src.slack_client import BasicSlackClient


def run_slackbot(
    query: QueryBase,
    dune: DuneClient,
    alert_client: PostClient,
    ping_frequency: int,
) -> None:
    """
    This is the main method of the program.
    Instantiate a query runner, and execute its run_loop
    """
    query_runner = QueryRunner(query, dune, alert_client, ping_frequency)
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

    alerter: PostClient
    if config.alert_type == AlertType.SLACK:
        alerter = BasicSlackClient(
            token=os.environ["SLACK_TOKEN"],
            # Use specified channel, or default to "global config"
            channel=config.alert_channel or os.environ["SLACK_ALERT_CHANNEL"],
        )
    elif config.alert_type == AlertType.TWITTER:
        alerter = TwitterClient(
            credentials={
                "consumer_key": os.environ["CONSUMER_KEY"],
                "consumer_secret": os.environ["CONSUMER_SECRET"],
                "access_token": os.environ["ACCESS_TOKEN"],
                "access_token_secret": os.environ["ACCESS_TOKEN_SECRET"],
            }
        )
    else:
        raise ValueError(f"Invalid or unsupported AlertType {config.alert_type}")

    run_slackbot(
        query=config.query,
        dune=DuneClient(os.environ["DUNE_API_KEY"]),
        alert_client=alerter,
        ping_frequency=config.ping_frequency,
    )
