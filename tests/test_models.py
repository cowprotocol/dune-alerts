import datetime
import unittest

from datetime import timedelta

from duneapi.types import QueryParameter

from src.models import TimeWindow


class TestTimeWindow(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime.datetime(year=1985, month=3, day=10)

    def test_constructor(self):
        start = self.start
        self.assertEqual(TimeWindow(start).end, start + timedelta(hours=6))
        self.assertEqual(
            TimeWindow(start, length_hours=3).end, start + timedelta(hours=3)
        )

    def test_from_cfg(self):
        length = 1
        window = TimeWindow.from_cfg(
            {
                "offset": 1,
                "length": length,
            }
        )
        self.assertEqual(window.end - window.start, timedelta(hours=length))
        self.assertEqual(window.length, length)
        # Not sure if it makes sense to text the actual start since now() will evaluate differently...

    def test_next(self):
        window = TimeWindow(self.start)
        next_window = window.next()
        self.assertEqual(window.end, next_window.start)
        self.assertEqual(window.length, next_window.length)

    def test_as_query_params(self):
        window = TimeWindow(self.start)
        self.assertEqual(
            window.as_query_parameters(),
            [
                QueryParameter.date_type(name="StartTime", value=self.start),
                QueryParameter.date_type(
                    name="EndTime", value=self.start + timedelta(hours=window.length)
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
