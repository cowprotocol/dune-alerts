"""
Some generic models used throughout the project
"""
from __future__ import annotations

from datetime import datetime, timedelta

from duneapi.types import QueryParameter


class TimeWindow:
    """Handling date arithmetic and string conversions for datetime intervals"""

    def __init__(self, start: datetime, length_hours: int = 6):
        self.start = start
        self.end = self.start + timedelta(hours=length_hours)
        self.length = length_hours

    @classmethod
    def from_cfg(cls, cfg: dict[str, int]) -> TimeWindow:
        """Loads TimeWindow based on current time length and offset (both in hours)"""
        return cls(
            start=datetime.now() - timedelta(hours=cfg["offset"]),
            length_hours=cfg["length"],
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
