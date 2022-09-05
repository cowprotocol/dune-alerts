"""
Implementation of BaseQueryMonitor for "windowed" queries having StartTime and EndTime
"""
from __future__ import annotations
import logging.config
from datetime import datetime, timedelta

from dune_client.query import Query

from src.models import TimeWindow
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
        query: Query,
        window: TimeWindow,
        threshold: int = 0,
    ):
        super().__init__(query, threshold)
        self._set_window(window)
        # Need to update the Query Parameters
        self.query.params = self.query.parameters() + self.window.as_query_parameters()

    def _set_window(self, window: TimeWindow) -> None:
        if window.end > datetime.now() - timedelta(hours=2):
            log.warning(
                "window end time is beyond 2 hours in the past, "
                "some data may not yet be available"
            )
        self.window = window
