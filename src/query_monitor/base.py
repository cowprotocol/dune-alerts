"""
Abstract class containing Base/Default QueryMonitor attributes.
"""
from __future__ import annotations

import logging.config
from abc import ABC
from typing import Optional

from duneapi.api import DuneAPI
from duneapi.types import QueryParameter, DuneRecord

from src.slack_client import BasicSlackClient

log = logging.getLogger(__name__)
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)


class BaseQueryMonitor(ABC):
    """
    Abstract base class for Dune Query Monitoring.
    Contains several default/fallback methods,
    that are extended on in some implementations.
    """

    def __init__(
        self,
        name: str,
        query_id: int,
        params: Optional[list[QueryParameter]] = None,
        threshold: int = 0,
        # TODO - These useless trivial defaults are only temporary... I hope.
        slack_client: BasicSlackClient = BasicSlackClient("", ""),
        dune: DuneAPI = DuneAPI("", ""),
    ):
        self.query_id = query_id
        self.fixed_params = params if params else []
        self.name = name
        # Threshold for alert worthy number of results.
        self.threshold = threshold
        self.slack_client = slack_client
        self.dune = dune

    def result_url(self) -> str:
        """Returns a link to query results excluding fixed parameters"""
        return f"https://dune.com/queries/{self.query_id}"

    def refresh(self) -> list[DuneRecord]:
        """Executes dune query by ID, and fetches the results by job ID returned"""
        # TODO - this could probably live in the base duneapi library.
        job_id = self.dune.execute(self.query_id, self.parameters())
        return self.dune.get_results(job_id)

    def parameters(self) -> list[QueryParameter]:
        """
        Base implementation only has fixed parameters,
        extensions (like WindowedQueryMonitor) would append additional parameters to the fixed ones
        """
        return self.fixed_params

    def alert_message(self, results: list[dict[str, str]]) -> str:
        """
        Default Alert message if not special implementation is provided.
        Says which query returned how many results along with a link to Dune.
        """
        num_results = len(results)
        return (
            f"{self.name} - detected {num_results} cases. "
            f"Results available at {self.result_url()}"
        )

    def alert_or_log(
        self, alert_condition: bool, alert_message: str, log_message: str
    ) -> None:
        """Post message if alert_condition is met, otherwise logs info."""
        if alert_condition:
            log.info(alert_message)
            self.slack_client.post(alert_message)
        else:
            log.info(log_message)

    def run_loop(self) -> None:
        """
        Standard run-loop refreshing query, fetching results and alerting if necessary.
        """
        log.info(f'Refreshing "{self.name}" query {self.result_url()}')
        results = self.refresh()
        self.alert_or_log(
            alert_condition=len(results) > self.threshold,
            alert_message=self.alert_message(results),
            log_message=f"No {self.name} detected",
        )


class QueryMonitor(BaseQueryMonitor):
    """This is essentially the base query monitor with all default methods"""
