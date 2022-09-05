"""Implementation of BaseQueryMonitor for queries beginning from StartTime"""
from __future__ import annotations
import urllib.parse

from dune_client.query import Query

from src.models import LeftBound
from src.query_monitor.result_threshold import ResultThresholdQuery


class LeftBoundedQueryMonitor(ResultThresholdQuery):
    """
    All queries here, must have `StartTime` as parameter.
    This is set by an instance's left_bound attribute.
    """

    def __init__(
        self,
        query: Query,
        left_bound: LeftBound,
        threshold: int = 0,
    ):
        super().__init__(query, threshold)
        self.left_bound = left_bound
        self.query.params = self.query.parameters() + left_bound.as_query_parameters()

    def result_url(self) -> str:
        """Returns a link to the query"""
        base = super().result_url()
        # Include variable parameters in the URL so they are set
        query = "&".join(
            [f"{p.key}={p.value}" for p in self.left_bound.as_query_parameters()]
        )
        return "?".join([base, urllib.parse.quote_plus(query, safe="=&?")])
