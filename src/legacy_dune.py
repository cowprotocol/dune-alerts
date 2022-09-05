""""
Basic Dune Client Class responsible for refreshing Dune Queries
Framework built on Dune's API Documentation
https://duneanalytics.notion.site/API-Documentation-1b93d16e0fa941398e15047f643e003a
"""
from duneapi.api import DuneAPI
from duneapi.types import DuneRecord
from dune_client.interface import DuneInterface
from dune_client.query import Query


# TODO - Move This into dune_client.
class LegacyDuneClient(DuneInterface):
    """Implementation of DuneInterface using the "legacy" (browser emulator) duneapi"""

    def __init__(self, dune: DuneAPI):
        self.dune = dune

    def refresh(self, query: Query) -> list[DuneRecord]:
        """Executes dune query by ID, and fetches the results by job ID returned"""
        job_id = self.dune.execute(query.query_id, query.parameters())
        return self.dune.get_results(job_id)
