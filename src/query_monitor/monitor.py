"""
Abstract class containing Base/Default QueryMonitor attributes.
"""
from __future__ import annotations

import logging.config

from duneapi.api import DuneAPI
from duneapi.types import DuneRecord
from slack.web.client import WebClient

from src.query_monitor.alert_type import AlertType
from src.query_monitor.base_query import NoResultsQuery
from src.slack_client import BasicSlackClient

log = logging.getLogger(__name__)
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)


class QueryMonitor:
    query: NoResultsQuery
    dune: DuneAPI
    slack_client: BasicSlackClient

    def refresh(self) -> list[DuneRecord]:
        """Executes dune query by ID, and fetches the results by job ID returned"""
        # TODO - this could probably live in the base duneapi library.
        log.info(f'Refreshing "{self.query.name}" query {self.query.result_url()}')
        job_id = self.dune.execute(self.query.query_id, self.query.parameters())
        return self.dune.get_results(job_id)

    def run_loop(self) -> None:
        """
        Standard run-loop refreshing query, fetching results and alerting if necessary.
        """
        results = self.refresh()
        alert = self.query.alert_message(results)
        if alert.kind == AlertType.SLACK:
            log.warning(alert.value)
            self.slack_client.post(alert.value)
        elif alert.kind == AlertType.LOG:
            log.info(alert.value)
