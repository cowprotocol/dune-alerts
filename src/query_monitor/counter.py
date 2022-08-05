"""QueryMonitor for Counters. Alert set to valuation"""

from typing import Optional

from duneapi.types import QueryParameter

from src.query_monitor.base import BaseQueryMonitor
from src.logging import set_log

log = set_log(__name__)


class CounterQueryMonitor(BaseQueryMonitor):
    """
    All queries here, must return a single record specifying a column with numeric type.
    """

    def __init__(
        self,
        name: str,
        query_id: int,
        column: str,
        alert_value: float = 0.0,
        params: Optional[list[QueryParameter]] = None,
    ):
        super().__init__(name, query_id, params)
        self.column = column
        self.alert_value = alert_value

    def alert_message(self, results: list[dict[str, str]]) -> str:
        return (
            f"Query {self.name}: {self.column} exceeds {self.alert_value} "
            f"with {self._result_value(results)} (cf. {self.result_url()})"
        )

    def _result_value(self, results: list[dict[str, str]]) -> float:
        assert len(results) == 1, f"Expected single record, got {results}"
        return float(results[0][self.column])

    def run_loop(self) -> None:
        """
        Special run-loop refreshing query, fetching results and alerting if necessary.
        """
        log.info(f'Refreshing "{self.name}" query {self.result_url()}')
        results = self.refresh()
        result_value = self._result_value(results)
        self.alert_or_log(
            alert_condition=result_value > self.alert_value,
            alert_message=self.alert_message(results),
            log_message=f"value of {self.column} = {result_value} "
            f"does not exceed {self.alert_value}",
        )
