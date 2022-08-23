from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class AlertType(Enum):
    SLACK = 0
    LOG = 1
    NONE = 2


@dataclass
class Alert:
    kind: AlertType
    value: str

    @classmethod
    def default(cls) -> Alert:
        return Alert(AlertType.NONE, "")


