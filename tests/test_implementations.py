import datetime
import unittest

from duneapi.types import QueryParameter

from src.models import TimeWindow
from src.query_monitor.base import QueryMonitor
from src.query_monitor.factory import load_from_config
from src.query_monitor.windowed import WindowedQueryMonitor
from src.query_monitor.left_bounded import LeftBoundedQueryMonitor


class TestQueryMonitor(unittest.TestCase):
    def setUp(self) -> None:
        self.date = datetime.datetime(year=1985, month=3, day=10)
        self.query_params = [
            QueryParameter.enum_type("Enum", "option1", ["option1", "option2"]),
            QueryParameter.text_type("Text", "option1"),
            QueryParameter.number_type("Text", 12),
            QueryParameter.date_type("Date", "2021-01-01 12:34:56"),
        ]
        self.monitor = QueryMonitor(
            name="Monitor", query_id=0, params=self.query_params
        )
        self.windowed_monitor = WindowedQueryMonitor(
            name="Windowed Monitor",
            query_id=1,
            window=TimeWindow(start=self.date),
            params=self.query_params,
        )

    def test_result_url(self):
        self.assertEqual(self.monitor.result_url(), "https://dune.com/queries/0")
        self.assertEqual(
            self.windowed_monitor.result_url(),
            "https://dune.com/queries/1?StartTime=1985-03-10+00%3A00%3A00&EndTime=1985-03-10+06%3A00%3A00",
        )

    def test_parameters(self):
        self.assertEqual(self.monitor.parameters(), self.query_params)
        self.assertEqual(
            self.windowed_monitor.parameters(),
            self.query_params + self.windowed_monitor.window.as_query_parameters(),
        )

    def test_alert_message(self):
        self.assertEqual(
            self.monitor.alert_message([{}]),
            f"{self.monitor.name} - detected 1 cases. "
            f"Results available at {self.monitor.result_url()}",
        )

        self.assertEqual(
            self.windowed_monitor.alert_message([{}, {}]),
            f"{self.windowed_monitor.name} - detected 2 cases. "
            f"Results available at {self.windowed_monitor.result_url()}",
        )


class TestFactory(unittest.TestCase):
    def test_load_from_config(self):
        no_params_monitor = load_from_config("./tests/data/no-params.yaml")
        self.assertTrue(isinstance(no_params_monitor, QueryMonitor))
        self.assertEqual(no_params_monitor.parameters(), [])

        with_params_monitor = load_from_config("./tests/data/with-params.yaml")
        self.assertGreater(len(with_params_monitor.parameters()), 0)
        self.assertTrue(isinstance(with_params_monitor, QueryMonitor))

        windowed_monitor = load_from_config("./tests/data/windowed-query.yaml")
        self.assertTrue(isinstance(windowed_monitor, WindowedQueryMonitor))

        day_window_monitor = load_from_config("./tests/data/day-window.yaml")
        self.assertTrue(isinstance(day_window_monitor, WindowedQueryMonitor))

        left_bounded_monitor = load_from_config("./tests/data/left-bounded.yaml")
        self.assertTrue(isinstance(left_bounded_monitor, LeftBoundedQueryMonitor))


if __name__ == "__main__":
    unittest.main()
