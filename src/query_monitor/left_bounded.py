"""Implementation of BaseQueryMonitor for queries beginning from StartTime"""
from __future__ import annotations
import urllib.parse
from enum import Enum

from duneapi.types import QueryParameter

from src.query_monitor.base import QueryData
from src.query_monitor.result_threshold import ResultThresholdQuery


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
        return [str(e.value) for e in cls]


class LeftBound:
    """Left Bound for Query Monitor"""

    def __init__(self, units: TimeUnit, offset: int):
        self.units = units
        self.offset = offset

    def as_query_parameters(self) -> list[QueryParameter]:
        """Returns DuneQueryParameters for object instance"""
        return [
            QueryParameter.enum_type(
                name="TimeUnits",
                value=str(self.units.value),
                options=TimeUnit.options(),
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


class LeftBoundedQueryMonitor(ResultThresholdQuery):
    """
    All queries here, must have `StartTime` as parameter.
    This is set by an instance's left_bound attribute.
    """

    def __init__(
        self,
        query: QueryData,
        left_bound: LeftBound,
        threshold: int = 0,
    ):
        super().__init__(query, threshold)
        self.left_bound = left_bound

    def parameters(self) -> list[QueryParameter]:
        """Similar to the base model, but with left bound parameter appended"""
        return (self.query.params or []) + self.left_bound.as_query_parameters()

    def result_url(self) -> str:
        """Returns a link to the query"""
        base = super().result_url()
        # Include variable parameters in the URL so they are set
        query = "&".join(
            [f"{p.key}={p.value}" for p in self.left_bound.as_query_parameters()]
        )
        return "?".join([base, urllib.parse.quote_plus(query, safe="=&?")])
