""""
Basic Dune Client Class responsible for refreshing Dune Queries
Framework built on Dune's API Documentation
https://duneanalytics.notion.site/API-Documentation-1b93d16e0fa941398e15047f643e003a
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import requests
from duneapi.types import DuneRecord

from src.query_monitor.base import QueryBase

BASE_URL = "https://api.dune.com/api/v1"


class ExecutionState(Enum):
    """
    Enum for possible values of Query Execution
    """

    PENDING = "QUERY_STATE_PENDING"
    COMPLETED = "QUERY_STATE_COMPLETED"


@dataclass
class ExecutionResponse:
    """
    Representation of Response from Dune's [Post] Execute Query ID endpoint
    """

    execution_id: str
    state: ExecutionState

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> ExecutionResponse:
        """
        Sample Value:
        {
            "execution_id": "01GB1Y2MRA4C9PNQ0EQYVT4K6R",
            "state": "QUERY_STATE_PENDING"
        }
        """
        # TODO - isn't there a way to parse a dict directly into an instance
        return cls(
            execution_id=data["execution_id"], state=ExecutionState(data["state"])
        )


@dataclass
class ExecutionStatusResponse:
    """
    Representation of Response from Dune's [Get] Execution Status endpoint
    """

    execution_id: str
    query_id: int
    state: ExecutionState
    submitted_at: datetime
    expires_at: datetime
    execution_started_at: datetime

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> ExecutionStatusResponse:
        """
        Sample input.
        {
            "execution_id": "01GBM4W2N0NMCGPZYW8AYK4YF1",
            "query_id": 980708,
            "state": "QUERY_STATE_EXECUTING",
            "submitted_at": "2022-08-29T06:33:24.913138Z",
            "expires_at": "1970-01-01T00:00:00Z",
            "execution_started_at": "2022-08-29T06:33:24.916543331Z"
        }
        """
        # TODO - isn't there a way to parse a dict directly into an instance
        return cls(
            execution_id=data["execution_id"],
            query_id=int(data["query_id"]),
            state=ExecutionState(data["state"]),
            # TODO - parse the dates...
            submitted_at=datetime.now(),
            expires_at=datetime.now(),
            execution_started_at=datetime.now(),
        )


class DuneClient:
    """
    An interface for Dune API with a few convenience methods
    combining the use of endpoints (e.g. refresh)
    """

    def __init__(self, api_key: str):
        # TODO - not sure if better read the env here or if the caller should pass it.
        self.token = api_key  # os.environ["DUNE_API_KEY"]

    def execute(self, query: QueryBase) -> ExecutionResponse:
        """Post's to Dune API for execute `query`"""
        # https://duneanalytics.notion.site/API-Documentation-1b93d16e0fa941398e15047f643e003a
        raw_response = requests.post(
            url=f"{BASE_URL}/query/{query.query_id}/execute",
            params={
                "query_parameters": {
                    param.key: param.value for param in query.parameters()
                }
            },
            headers={"x-dune-api-key": self.token},
        )
        # TODO - log raw_response
        return ExecutionResponse.from_dict(raw_response.json())

    def get_status(self, job_id: str) -> ExecutionStatusResponse:
        """GET status from Dune API for `job_id` (aka `execution_id`)"""
        raw_response = requests.get(
            url=f"{BASE_URL}/execution/{job_id}/status",
            headers={"x-dune-api-key": self.token},
        )
        # TODO - log raw_response
        return ExecutionStatusResponse.from_dict(raw_response.json())

    def get_results(self, job_id: str) -> list[DuneRecord]:
        """GET results from Dune API for `job_id` (aka `execution_id`)"""
        raw_response = requests.get(
            url=f"{BASE_URL}/execution/{job_id}/results",
            headers={"x-dune-api-key": self.token},
        )
        # TODO - log raw_response
        # TODO - define a class representing Full Response
        results: list[DuneRecord] = raw_response.json()["result"]["rows"]
        return results

    def refresh(self, query: QueryBase) -> list[DuneRecord]:
        """
        Executes a Dune query, waits till query execution completes,
        fetches and returns the results.
        *Sleeps 3 seconds inbetween each request*.
        """
        job_id = self.execute(query).execution_id
        while self.get_status(job_id).state == ExecutionState.PENDING:
            print("waiting for query execution to complete!")
            # TODO - use a better model for status pings.
            time.sleep(3)

        return self.get_results(job_id)
