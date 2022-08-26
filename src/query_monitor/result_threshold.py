"""
Elementary implementation of QueryBase that alerts when
number of results returned is > `threshold`
"""
from duneapi.types import QueryParameter, DuneRecord

from src.alert import Alert, AlertLevel
from src.query_monitor.base import QueryBase, QueryData


class ResultThresholdQuery(QueryBase):
    """This is essentially the base query monitor with all default methods"""

    def __init__(self, query: QueryData, threshold: int = 0):
        super().__init__(query)
        self.threshold = threshold

    def parameters(self) -> list[QueryParameter]:
        """
        Base implementation only has fixed parameters,
        extensions (like WindowedQueryMonitor) would append additional parameters to the fixed ones
        """
        return self.query.params or []

    def alert_message(self, results: list[DuneRecord]) -> Alert:
        """
        Default Alert message if not special implementation is provided.
        Says which query returned how many results along with a link to Dune.
        """
        num_results = len(results)
        if num_results > self.threshold:
            return Alert(
                kind=AlertLevel.SLACK,
                value=f"{self.name} - detected {num_results} cases. "
                f"Results available at {self.result_url()}",
            )
        return Alert.default()
