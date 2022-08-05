"""
Main entry point to slackbot query monitoring
"""
import argparse
import os

import dotenv
from duneapi.api import DuneAPI

from src.query_monitor.factory import load_from_config
from src.slack_client import BasicSlackClient

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Missing Tokens")
    parser.add_argument(
        "--query-config",
        type=str,
        help="YAML configuration file for a QueryMonitor object",
        required=True,
    )
    args = parser.parse_args()

    dotenv.load_dotenv()
    query_monitor = load_from_config(args.query_config)
    # Set the third party communications to non-trivial after config instantiation
    query_monitor.slack_client = BasicSlackClient(
        token=os.environ["SLACK_TOKEN"], channel=os.environ["SLACK_ALERT_CHANNEL"]
    )
    query_monitor.dune = DuneAPI.new_from_environment()
    query_monitor.run_loop()
