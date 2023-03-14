"""Abstraction for posting alerts"""
from abc import ABC, abstractmethod


class PostClient(ABC):
    """
    Basic Post Client with message post functionality
    """

    @abstractmethod
    def post(self, message: str) -> None:
        """Posts `message` to `self.channel` excluding link previews."""
