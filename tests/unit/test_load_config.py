import os
import unittest

from src.query_monitor.factory import load_config
from tests.file import filepath


class TestConfigLoading(unittest.TestCase):
    def test_default_config(self):

        config = load_config(filepath("counter.yaml"))
        self.assertEqual(config.alert_channel, None)

    def test_specified_channel(self):
        config = load_config(filepath("alert-channel.yaml"))
        self.assertEqual(config.alert_channel, "Specific Channel")

    def test_ping_frequency(self):
        # Specified frequency
        config = load_config(filepath("ping-frequency.yaml"))
        self.assertEqual(config.ping_frequency, 28)

        # Default (not specified)
        config = load_config(filepath("counter.yaml"))
        self.assertEqual(config.ping_frequency, 20)


if __name__ == "__main__":
    unittest.main()
