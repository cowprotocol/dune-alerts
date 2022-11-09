import os
import unittest

from src.query_monitor.factory import load_config
from tests.file import filepath


class TestConfigLoading(unittest.TestCase):
    def setUp(self) -> None:
        self.fallback_alert_channel = "Default"
        os.environ["SLACK_ALERT_CHANNEL"] = self.fallback_alert_channel

    def test_default_config(self):

        config = load_config(filepath("counter.yaml"))
        self.assertEqual(config.alert_channel, self.fallback_alert_channel)

    def test_specified_channel(self):
        config = load_config(filepath("alert-channel.yaml"))
        self.assertEqual(config.alert_channel, "Specific Channel")


if __name__ == "__main__":
    unittest.main()
