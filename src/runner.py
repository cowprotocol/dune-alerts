"""
Query Runner takes any implementation of QueryBase, a dune connection and slack client.
It is responsible for refreshing the query, fetching results,
passing results onto the query and alerting when necessary.
"""
from __future__ import annotations

import logging.config

from src.alert import AlertLevel
from src.dune_interface import DuneInterface
from src.query_monitor.base import QueryBase
from src.slack_client import BasicSlackClient

log = logging.getLogger(__name__)
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)


class QueryRunner:
    """
    Refreshes a Dune Query, fetches results and alerts slack if necessary
    """

    def __init__(
        self, query: QueryBase, dune: DuneInterface, slack_client: BasicSlackClient
    ):
        self.query = query
        self.dune = dune
        self.slack_client = slack_client

    def run_loop(self) -> None:
        """
        Standard run-loop refreshing query, fetching results and alerting if necessary.
        """
        query = self.query
        log.info(f'Refreshing "{query.name}" query {query.result_url()}')
        results = self.dune.refresh(query)
        alert = query.get_alert(results)
        if alert.level == AlertLevel.SLACK:
            log.warning(alert.message)
            self.slack_client.post(alert.message)
        elif alert.level == AlertLevel.LOG:
            log.info(alert.message)
