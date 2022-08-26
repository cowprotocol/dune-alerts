"""
Implementation of BaseQueryMonitor for "windowed" queries having StartTime and EndTime
"""
from __future__ import annotations
import logging.config
import urllib.parse
from datetime import datetime, timedelta, date

from duneapi.types import QueryParameter

from src.query_monitor.base import QueryData
from src.query_monitor.result_threshold import ResultThresholdQuery

log = logging.getLogger(__name__)
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)


class TimeWindow:
    """Handling date arithmetic and string conversions for datetime intervals"""

    def __init__(self, start: datetime, length_hours: int = 6):
        self.start = start
        self.end = self.start + timedelta(hours=length_hours)
        self.length = length_hours

    @classmethod
    def from_cfg(cls, cfg: dict[str, int] | str) -> TimeWindow:
        """
        Loads TimeWindow based on current time and either one of two configurations
         1. `length` of time window and `offset` (both in hours)
         2. `yesterday` returning a full date interval
        """
        if isinstance(cfg, dict):
            return cls(
                start=datetime.now() - timedelta(hours=cfg["offset"]),
                length_hours=cfg["length"],
            )
        assert cfg == "yesterday"
        return TimeWindow.for_day(date.today() - timedelta(days=1))

    @classmethod
    def for_day(cls, day: date) -> TimeWindow:
        """
        Constructs TimeWindow for given day
        (i.e. 24 time window beginning at midnight on specified day)
        """
        return cls(
            # this is datetime object from date
            start=datetime.combine(day, datetime.min.time()),
            length_hours=24,
        )

    def as_query_parameters(self) -> list[QueryParameter]:
        """Dune query parameters defined by the start and end of the window"""
        return [
            QueryParameter.date_type(name="StartTime", value=self.start),
            QueryParameter.date_type(name="EndTime", value=self.end),
        ]

    def next(self) -> TimeWindow:
        """Returns a TimeWindow beginning from the end of self with same length"""
        return TimeWindow(start=self.end, length_hours=self.length)


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
