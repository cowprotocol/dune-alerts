"""
Implementation of BaseQueryMonitor for "windowed" queries having StartTime and EndTime
"""
from __future__ import annotations
import logging.config
import urllib.parse
from datetime import datetime, timedelta

from duneapi.types import QueryParameter

from src.models import TimeWindow
from src.query_monitor.base import QueryData
from src.query_monitor.result_threshold import ResultThresholdQuery

log = logging.getLogger(__name__)
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)


class WindowedQueryMonitor(ResultThresholdQuery):
    """
    All queries here, must have `StartTime` and `EndTime` as parameters,
    set by an instance's window attribute via window.as_query_parameters()
    """

    window: TimeWindow

    def __init__(
        self,
        query: QueryData,
        window: TimeWindow,
        threshold: int = 0,
    ):
        super().__init__(query, threshold)
        self._set_window(window)

    def parameters(self) -> list[QueryParameter]:
        """Similar to the base model, but with window parameters appended"""
        return (self.query.params or []) + self.window.as_query_parameters()

    def result_url(self) -> str:
        """Returns a link to the query"""
        base = super().result_url()
        # Include variable parameters in the URL so they are set
        query = "&".join(
            [f"{p.key}={p.value}" for p in self.window.as_query_parameters()]
        )
        return "?".join([base, urllib.parse.quote_plus(query, safe="=&?")])

    def _set_window(self, window: TimeWindow) -> None:
        if window.end > datetime.now() - timedelta(hours=2):
            log.warning(
                "window end time is beyond 2 hours in the past, some data may not yet be available"
            )
        self.window = window
