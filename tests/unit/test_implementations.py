import datetime
import os
import unittest

from dune_client.query import Query
from dune_client.types import QueryParameter

from src.alert import Alert, AlertLevel
from src.query_monitor.counter import CounterQueryMonitor
from src.query_monitor.factory import load_config
from src.query_monitor.result_threshold import ResultThresholdQuery
from src.query_monitor.windowed import WindowedQueryMonitor, TimeWindow
from src.query_monitor.left_bounded import LeftBoundedQueryMonitor
from tests.file import filepath


class TestQueryMonitor(unittest.TestCase):
    def setUp(self) -> None:
        self.date = datetime.datetime(year=1985, month=3, day=10)
        self.query_params = [
            QueryParameter.enum_type("Enum", "option1"),
            QueryParameter.text_type("Text", "plain text"),
            QueryParameter.number_type("Number", 12),
            QueryParameter.date_type("Date", "2021-01-01 12:34:56"),
        ]
        self.monitor = ResultThresholdQuery(
            query=Query(name="Monitor", query_id=0, params=self.query_params)
        )
        self.windowed_monitor = WindowedQueryMonitor(
            query=Query(name="Windowed Monitor", query_id=0, params=self.query_params),
            window=TimeWindow(start=self.date),
        )
        self.counter = CounterQueryMonitor(
            query=Query(name="Counter Monitor", query_id=0, params=self.query_params),
            column="col_name",
            alert_value=1.0,
        )

    def test_parameters(self):
        self.assertEqual(self.monitor.parameters(), self.query_params)
        self.assertEqual(
            self.windowed_monitor.parameters(),
            self.query_params + self.windowed_monitor.window.as_query_parameters(),
        )

    def test_alert_message(self):
        self.assertEqual(
            self.monitor.get_alert([{}]),
            Alert(
                level=AlertLevel.SLACK,
                message=f"{self.monitor.name} - detected 1 cases. "
                f"Results available at {self.monitor.result_url()}",
            ),
        )

        self.assertEqual(
            self.windowed_monitor.get_alert([{}, {}]),
            Alert(
                level=AlertLevel.SLACK,
                message=f"{self.windowed_monitor.name} - detected 2 cases. "
                f"Results available at {self.windowed_monitor.result_url()}",
            ),
        )

        ctr = self.counter
        self.assertEqual(
            ctr.get_alert([{ctr.column: ctr.alert_value + 1}]),
            Alert(
                level=AlertLevel.SLACK,
                message=f"Query Counter Monitor: {ctr.column} exceeds {ctr.alert_value} "
                f"with {ctr.alert_value + 1} (cf. {ctr.result_url()})",
            ),
        )

        with self.assertRaises(AssertionError):
            self.counter._result_value([])
        with self.assertRaises(KeyError):
            self.counter._result_value([{}])


class TestFactory(unittest.TestCase):
    def test_load_from_config(self):
        os.environ["SLACK_ALERT_CHANNEL"] = "dummy channel"
        no_params_monitor = load_config(filepath("no-params.yaml")).query
        self.assertTrue(isinstance(no_params_monitor, ResultThresholdQuery))
        self.assertEqual(no_params_monitor.parameters(), [])

        with_params_monitor = load_config(filepath("with-params.yaml")).query
        self.assertGreater(len(with_params_monitor.parameters()), 0)
        self.assertTrue(isinstance(with_params_monitor, ResultThresholdQuery))

        windowed_monitor = load_config(filepath("windowed-query.yaml")).query
        self.assertTrue(isinstance(windowed_monitor, WindowedQueryMonitor))

        day_window_monitor = load_config(filepath("day-window.yaml")).query
        self.assertTrue(isinstance(day_window_monitor, WindowedQueryMonitor))

        left_bounded_monitor = load_config(filepath("left-bounded.yaml")).query
        self.assertTrue(isinstance(left_bounded_monitor, LeftBoundedQueryMonitor))
        del os.environ["SLACK_ALERT_CHANNEL"]

    def test_load_config_error(self):
        with self.assertRaises(KeyError):
            load_config(filepath("no-params.yaml"))


if __name__ == "__main__":
    unittest.main()
