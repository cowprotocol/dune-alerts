"""
Elementary implementation of QueryBase that alerts when
number of results returned is > `threshold`
"""
from duneapi.types import DuneRecord
from dune_client.query import Query

from src.alert import Alert, AlertLevel
from src.query_monitor.base import QueryBase


class ResultThresholdQuery(QueryBase):
    """This is essentially the base query monitor with all default methods"""

    def __init__(self, query: Query, threshold: int = 0):
        super().__init__(query)
        self.threshold = threshold

    def get_alert(self, results: list[DuneRecord]) -> Alert:
        """
        Default Alert message if not special implementation is provided.
        Says which query returned how many results along with a link to Dune.
        """
        num_results = len(results)
        if num_results > self.threshold:
            return Alert(
                level=AlertLevel.SLACK,
                message=f"{self.name} - detected {num_results} cases. "
                f"Results available at {self.result_url()}",
            )
        return Alert.default()
