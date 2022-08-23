from abc import ABC
from dataclasses import dataclass
from typing import Optional

from duneapi.types import QueryParameter, DuneRecord

from src.query_monitor.alert_type import Alert, AlertType


@dataclass
class Query:
    name: str
    query_id: int
    params: Optional[list[QueryParameter]] = None


class QueryMonitor(ABC):
    """
    Base class for Dune Query.
    that are extended on in some implementations.
    """

    def __init__(self, query: Query):
        self.query = query

    @property
    def query_id(self) -> int:
        return self.query.query_id

    @property
    def name(self) -> str:
        return self.query.name

    def parameters(self) -> list[QueryParameter]:
        """
        Base implementation only has fixed parameters,
        extensions (like WindowedQueryMonitor) would append additional parameters to the fixed ones
        """
        # return self.query.params

    def result_url(self) -> str:
        """Returns a link to query results excluding fixed parameters"""
        # return f"https://dune.com/queries/{self.query_id}"

    def alert_message(self, results: list[DuneRecord]) -> Alert:
        """
        Default Alert message if not special implementation is provided.
        Says which query returned how many results along with a link to Dune.
        """
        # num_results = len(results)
        # if num_results > 0:
        #     return Alert(
        #         kind=AlertType.SLACK,
        #         value=f"{self.name} - detected {num_results} cases. "
        #         f"Results available at {self.result_url()}",
        #     )
        # return Alert.default()


class ResultThresholdQuery(QueryMonitor):
    """This is essentially the base query monitor with all default methods"""

    def __init__(self, query: Query, threshold: int = 0):
        super().__init__(query)
        self.threshold = threshold

    def parameters(self) -> list[QueryParameter]:
        """
        Base implementation only has fixed parameters,
        extensions (like WindowedQueryMonitor) would append additional parameters to the fixed ones
        """
        return self.query.params

    def result_url(self) -> str:
        """Returns a link to query results excluding fixed parameters"""
        return f"https://dune.com/queries/{self.query_id}"

    def alert_message(self, results: list[DuneRecord]) -> Alert:
        """
        Default Alert message if not special implementation is provided.
        Says which query returned how many results along with a link to Dune.
        """
        num_results = len(results)
        if num_results > self.threshold:
            return Alert(
                kind=AlertType.SLACK,
                value=f"{self.name} - detected {num_results} cases. "
                f"Results available at {self.result_url()}",
            )
        return Alert.default()
