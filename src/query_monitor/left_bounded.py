"""Implementation of BaseQueryMonitor for queries beginning from StartTime"""
from __future__ import annotations

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
