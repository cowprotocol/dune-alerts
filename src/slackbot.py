"""
Main entry point to slackbot query monitoring
"""
import argparse
import os
import ssl

import certifi
import dotenv
from duneapi.api import DuneAPI
from slack.web.client import WebClient

from src.query_monitor.factory import load_from_config

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

    query_monitor.run_loop(
        dune=DuneAPI.new_from_environment(),
        slack_client=WebClient(
            token=os.environ["SLACK_TOKEN"],
            # https://stackoverflow.com/questions/59808346/python-3-slack-client-ssl-sslcertverificationerror
            ssl=ssl.create_default_context(cafile=certifi.where()),
        ),
        alert_channel=os.environ["SLACK_ALERT_CHANNEL"],
    )
