"""
Enum for alert levels and data class of type
(AlertLevel, String) containing the alert message
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class AlertLevel(Enum):
    """
    Alert Levels ranging from
    None (the lowest) to Slack (the highest)
    """

    NONE = 0
    LOG = 1
    SLACK = 2


@dataclass
class Alert:
    """Encodes a "tuple" of AlertLevel with a message"""

    level: AlertLevel
    message: str

    @classmethod
    def default(cls) -> Alert:
        """Default alert level is non with no message."""
        return cls(AlertLevel.NONE, "")

    @classmethod
    def log(cls, message: str) -> Alert:
        """Easy Log Constructor"""
        return cls(AlertLevel.LOG, message)

    @classmethod
    def slack(cls, message: str) -> Alert:
        """Easy Slack variant constructor"""
        return cls(AlertLevel.SLACK, message)
