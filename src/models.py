"""
Some generic models used throughout the project
"""
from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum

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


class TimeUnit(Enum):
    """
    Enum representing SQL interval time units
    """

    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"

    @classmethod
    def options(cls) -> list[str]:
        """Returns a list of all available enum items"""
        return [e.value for e in cls]


class LeftBound:
    """Left Bound for Query Monitor"""

    def __init__(self, units: TimeUnit, offset: int):
        self.units = units
        self.offset = offset

    def as_query_parameters(self) -> list[QueryParameter]:
        """Returns DuneQueryParameters for object instance"""
        return [
            QueryParameter.enum_type(
                name="TimeUnits", value=self.units.value, options=TimeUnit.options()
            ),
            QueryParameter.number_type(name="Offset", value=self.offset),
        ]

    @classmethod
    def from_cfg(cls, cfg: dict[str, int]) -> LeftBound:
        """Loads LeftBound based on dict containing keys units and offset"""
        return cls(
            units=TimeUnit(cfg["units"]),
            offset=int(cfg["offset"]),
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LeftBound):
            return self.units == other.units and self.offset == other.offset
        raise ValueError(f"Can't compare LeftBound with {type(other)}")
