"""
Main entry point to slackbot query monitoring
"""
import argparse
import os

import dotenv
from duneapi.api import DuneAPI

from src.query_monitor.factory import load_from_config
from src.runner import QueryRunner
from src.slack_client import BasicSlackClient


def run_slackbot(config_yaml: str) -> None:
    """
    This is the main method of the program.
    Instantiate a query runner, and execute its run_loop
    """
    dotenv.load_dotenv()
    query_runner = QueryRunner(
        query=load_from_config(config_yaml),
        dune=DuneAPI.new_from_environment(),
        slack_client=BasicSlackClient(
            token=os.environ["SLACK_TOKEN"], channel=os.environ["SLACK_ALERT_CHANNEL"]
        ),
    )
    query_runner.run_loop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Missing Tokens")
    parser.add_argument(
        "--query-config",
        type=str,
        help="YAML configuration file for a QueryMonitor object",
        required=True,
    )
    args = parser.parse_args()
    run_slackbot(args.query_config)
