"""Implementation of BaseQueryMonitor for queries beginning from StartTime"""
import urllib.parse
from typing import Optional

from duneapi.types import QueryParameter

from src.models import LeftBound
from src.query_monitor.base import BaseQueryMonitor


class LeftBoundedQueryMonitor(BaseQueryMonitor):
    """
    All queries here, must have `StartTime` as parameter.
    This is set by an instance's left_bound attribute.
    """

    def __init__(
        self,
        name: str,
        query_id: int,
        left_bound: LeftBound,
        params: Optional[list[QueryParameter]] = None,
        threshold: int = 0,
    ):
        super().__init__(name, query_id, params, threshold)
        self.left_bound = left_bound

    def parameters(self) -> list[QueryParameter]:
        """Similar to the base model, but with left bound parameter appended"""
        return self.fixed_params + self.left_bound.as_query_parameters()

    def result_url(self) -> str:
        """Returns a link to the query"""
        base = super().result_url()
        # Include variable parameters in the URL so they are set
        query = "&".join(
            [f"{p.key}={p.value}" for p in self.left_bound.as_query_parameters()]
        )
        return "?".join([base, urllib.parse.quote_plus(query, safe="=&?")])
