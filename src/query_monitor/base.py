"""
Abstract class containing Base/Default QueryMonitor attributes.
"""
from abc import ABC, abstractmethod

from dune_client.types import DuneRecord
from dune_client.query import Query


from src.alert import Alert


class QueryBase(ABC):
    """
    Base class for Dune Query.
    that are extended on in some implementations.
    """

    def __init__(self, query: Query):
        self.query = query

    @property
    def query_id(self) -> int:
        """Returns (nested) query ID - for easier access"""
        return self.query.query_id

    @property
    def name(self) -> str:
        """Returns (nested) query name - for easier access"""
        return self.query.name

    def result_url(self) -> str:
        """Returns a link to query results excluding fixed parameters"""
        return f"https://dune.com/queries/{self.query_id}"

    @abstractmethod
    def get_alert(self, results: list[DuneRecord]) -> Alert:
        """
        Default Alert message if not special implementation is provided.
        Says which query returned how many results along with a link to Dune.
        """
