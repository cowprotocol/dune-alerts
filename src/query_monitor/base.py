"""
Abstract class containing Base/Default QueryMonitor attributes.
"""
from __future__ import annotations

import logging.config
from abc import ABC
from typing import Optional

from duneapi.api import DuneAPI
from duneapi.types import QueryParameter, DuneRecord
from slack.web.client import WebClient

log = logging.getLogger(__name__)
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)


class BaseQueryMonitor(ABC):
    """
    Abstract base class for Dune Query Monitoring.
    Contains several default/fallback methods,
    that are extended on in some implementations.
    """

    def __init__(
        self, name: str, query_id: int, params: Optional[list[QueryParameter]] = None
    ):
        self.query_id = query_id
        self.fixed_params = params if params else []
        self.name = name

    def result_url(self) -> str:
        """Returns a link to query results excluding fixed parameters"""
        return f"https://dune.com/queries/{self.query_id}"

    def refresh(self, dune: DuneAPI) -> list[DuneRecord]:
        """Executes dune query by ID, and fetches the results by job ID returned"""
        # TODO - this could probably live in the base duneapi library.
        job_id = dune.execute(self.query_id, self.parameters())
        return dune.get_results(job_id)

    def parameters(self) -> list[QueryParameter]:
        """
        Base implementation only has fixed parameters,
        extensions (like WindowedQueryMonitor) would append additional parameters to the fixed ones
        """
        return self.fixed_params

    def alert_message(self, num_results: int) -> str:
        """
        Default Alert message if not special implementation is provided.
        Says which query returned how many results along with a link to Dune.
        """
        return (
            f"{self.name} - detected {num_results} cases. "
            f"Results available at {self.result_url()}"
        )

    def run_loop(
        self, dune: DuneAPI, slack_client: WebClient, alert_channel: str
    ) -> None:
        """
        Standard run-loop refreshing query, fetching results and alerting if necessary.
        """
        log.info(f'Refreshing "{self.name}" query {self.query_id}')
        results = self.refresh(dune)
        if results:
            log.error(self.alert_message(len(results)))
            slack_client.chat_postMessage(
                channel=alert_channel,
                text=self.alert_message(len(results)),
                # Do not show link preview!
                # https://api.slack.com/reference/messaging/link-unfurling
                unfurl_media=False,
            )
        else:
            log.info(f"No {self.name} detected")
