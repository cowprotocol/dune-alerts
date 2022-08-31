"""
Abstract class for a basic Dune Interface with refresh method used by Query Runner.
"""
from abc import ABC

from duneapi.api import DuneAPI
from duneapi.types import DuneRecord

from src.query_monitor.base import QueryBase


class DuneInterface(ABC):
    """
    User Facing Methods for a Dune Client
    """

    def refresh(self, query: QueryBase) -> list[DuneRecord]:
        """
        Executes a Dune query, waits till query execution completes,
        fetches and returns the results.
        """


class LegacyDuneClient(DuneInterface):
    """Implementation of DuneInterface using the "legacy" (browser emulator) duneapi"""

    def __init__(self, dune: DuneAPI):
        self.dune = dune

    def refresh(self, query: QueryBase) -> list[DuneRecord]:
        """Executes dune query by ID, and fetches the results by job ID returned"""
        job_id = self.dune.execute(query.query_id, query.parameters())
        return self.dune.get_results(job_id)
