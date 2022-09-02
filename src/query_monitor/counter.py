"""QueryMonitor for Counters. Alert set to valuation"""

from duneapi.types import DuneRecord
from dune_client.query import Query

from src.alert import Alert, AlertLevel
from src.query_monitor.base import QueryBase


class CounterQueryMonitor(QueryBase):
    """
    All queries here, must return a single record specifying a column with numeric type.
    """

    def __init__(
        self,
        query: Query,
        column: str,
        alert_value: float = 0.0,
    ):
        super().__init__(query)
        self.column = column
        self.alert_value = alert_value

    def _result_value(self, results: list[DuneRecord]) -> float:
        assert len(results) == 1, f"Expected single record, got {results}"
        return float(results[0][self.column])

    def get_alert(self, results: list[DuneRecord]) -> Alert:
        result_value = self._result_value(results)
        if result_value > self.alert_value:
            return Alert(
                level=AlertLevel.SLACK,
                message=f"Query {self.name}: {self.column} exceeds {self.alert_value} "
                f"with {self._result_value(results)} (cf. {self.result_url()})",
            )
        return Alert(
            level=AlertLevel.LOG,
            message=f"value of {self.column} = {result_value} "
            f"does not exceed {self.alert_value}",
        )
