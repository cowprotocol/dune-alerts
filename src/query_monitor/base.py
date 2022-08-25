"""
Abstract class containing Base/Default QueryMonitor attributes.
"""
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from duneapi.types import QueryParameter, DuneRecord

from src.query_monitor.alert_type import Alert


@dataclass
class QueryData:
    """Basic data structure constituting a Dune Analytics Query."""

    name: str
    query_id: int
    params: Optional[list[QueryParameter]] = None


class QueryBase(ABC):
    """
    Base class for Dune Query.
    that are extended on in some implementations.
    """

    def __init__(self, query: QueryData):
        self.query = query

    @property
    def query_id(self) -> int:
        """Returns (nested) query ID - for easier access"""
        return self.query.query_id

    @property
    def name(self) -> str:
        """Returns (nested) query name - for easier access"""
        return self.query.name

    def parameters(self) -> list[QueryParameter]:
        """
        Base implementation only has fixed parameters,
        extensions (like WindowedQueryMonitor) would append additional parameters to the fixed ones
        """

    def result_url(self) -> str:
        """Returns a link to query results excluding fixed parameters"""

    def alert_message(self, results: list[DuneRecord]) -> Alert:
        """
        Default Alert message if not special implementation is provided.
        Says which query returned how many results along with a link to Dune.
        """
