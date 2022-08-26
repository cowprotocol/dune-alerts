"""
Query Runner takes any implementation of QueryBase, a dune connection and slack client.
It is responsible for refreshing the query, fetching results,
passing results onto the query and alerting when necessary.
"""
from __future__ import annotations

import logging.config

from duneapi.api import DuneAPI
from duneapi.types import DuneRecord

from src.alert import AlertLevel
from src.query_monitor.base import QueryBase
from src.slack_client import BasicSlackClient

log = logging.getLogger(__name__)
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)


class QueryRunner:
    """
    Refreshes a Dune Query, fetches results and alerts slack if necessary
    """

    def __init__(self, query: QueryBase, dune: DuneAPI, slack_client: BasicSlackClient):
        self.query = query
        self.dune = dune
        self.slack_client = slack_client

    def refresh(self) -> list[DuneRecord]:
        """Executes dune query by ID, and fetches the results by job ID returned"""
        # TODO - this could probably live in the base duneapi library.
        query = self.query
        log.info(f'Refreshing "{query.name}" query {query.result_url()}')
        job_id = self.dune.execute(query.query_id, query.parameters())
        return self.dune.get_results(job_id)

    def run_loop(self) -> None:
        """
        Standard run-loop refreshing query, fetching results and alerting if necessary.
        """
        results = self.refresh()
        alert = self.query.alert_message(results)
        if alert.kind == AlertLevel.SLACK:
            log.warning(alert.value)
            self.slack_client.post(alert.value)
        elif alert.kind == AlertLevel.LOG:
            log.info(alert.value)
