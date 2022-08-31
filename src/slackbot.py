"""
Main entry point to slackbot query monitoring
"""
import argparse
import os

import dotenv
from duneapi.api import DuneAPI

from src.dune_interface import LegacyDuneClient
from src.dune_client import DuneClient
from src.query_monitor.factory import load_from_config
from src.runner import QueryRunner
from src.slack_client import BasicSlackClient


def run_slackbot(config_yaml: str, use_legacy_dune: bool) -> None:
    """
    This is the main method of the program.
    Instantiate a query runner, and execute its run_loop
    """
    dotenv.load_dotenv()
    query_runner = QueryRunner(
        query=load_from_config(config_yaml),
        dune=(
            LegacyDuneClient(DuneAPI.new_from_environment())
            if use_legacy_dune
            else DuneClient(os.environ["DUNE_API_KEY"])
        ),
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
    parser.add_argument(
        "--use-legacy-dune",
        type=bool,
        help="Indicate whether legacy duneapi client should be used",
        default=False,
    )
    args = parser.parse_args()
    run_slackbot(args.query_config, args.use_legacy_dune)
