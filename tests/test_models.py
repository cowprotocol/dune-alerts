import unittest

from datetime import timedelta, datetime

from duneapi.types import QueryParameter

from src.models import LeftBound, TimeUnit, TimeWindow


class TestTimeWindow(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime(year=1985, month=3, day=10)

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

        window = TimeWindow.from_cfg("yesterday")
        today = datetime.today().date()
        yesterday = today - timedelta(days=1)

        self.assertEqual(window.start, datetime.combine(yesterday, datetime.min.time()))
        # The above assertion is equivalent to
        # self.assertEqual(window.start.date(), yesterday)
        # self.assertEqual(datetime.strftime(window.start, "%H:%M:%S"), "00:00:00")

        self.assertEqual(window.end, datetime.combine(today, datetime.min.time()))

    def test_from_cfg_error(self):
        with self.assertRaises(AssertionError):
            TimeWindow.from_cfg("invalid input")

        with self.assertRaises(KeyError):
            TimeWindow.from_cfg({"bad_key": 1})

    def test_from_day(self):
        window = TimeWindow.for_day(self.start.date())

        self.assertEqual(window.start, self.start)
        self.assertEqual(window.end, self.start + timedelta(days=1))
        self.assertEqual(window.end, self.start + timedelta(hours=24))
        self.assertEqual(datetime.strftime(window.start, "%H:%M:%S"), "00:00:00")
        self.assertEqual(datetime.strftime(window.end, "%H:%M:%S"), "00:00:00")

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


class TestLeftBound(unittest.TestCase):
    def setUp(self) -> None:
        self.left_bound = LeftBound(TimeUnit("minutes"), 1)

    def test_constructor(self):
        self.assertEqual(self.left_bound.units, TimeUnit.MINUTES)
        self.assertEqual(self.left_bound.offset, 1)

    def test_from_cfg(self):
        self.assertEqual(
            LeftBound.from_cfg(
                {
                    "offset": 1,
                    "units": TimeUnit.MINUTES,
                }
            ),
            self.left_bound,
        )

    def test_as_query_params(self):
        self.assertEqual(
            self.left_bound.as_query_parameters(),
            [
                QueryParameter.enum_type(
                    name="TimeUnits",
                    value=str(TimeUnit.MINUTES.value),
                    options=TimeUnit.options(),
                ),
                QueryParameter.number_type(name="Offset", value=1),
            ],
        )


if __name__ == "__main__":
    unittest.main()
