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
from typing import Union, Optional, Any

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
        return cls(
            execution_id=data["execution_id"], state=ExecutionState(data["state"])
        )


@dataclass
class TimeData:
    """A collection of all timestamp related values contained within Dune Response"""

    submitted_at: datetime
    expires_at: datetime
    execution_started_at: datetime
    execution_ended_at: Optional[datetime]

    @staticmethod
    def parse(timestamp: str) -> datetime:
        """
        Sample Input:
        '2022-08-29T06:33:24.913138Z'
        """
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TimeData:
        """
        Sample Input:
        {
            "submitted_at": "2022-08-29T06:33:24.913138Z",
            "expires_at": "2024-08-28T06:36:41.58847Z",
            "execution_started_at": "2022-08-29T06:33:24.916543Z",
            "execution_ended_at": "2022-08-29T06:36:41.588467Z",
        }
        """
        parse = cls.parse
        end = data.get("execution_ended_at")
        return cls(
            submitted_at=parse(data["submitted_at"]),
            expires_at=parse(data["expires_at"]),
            execution_started_at=parse(data["execution_started_at"]),
            execution_ended_at=None if end is None else parse(end),
        )


@dataclass
class ExecutionStatusResponse:
    """
    Representation of Response from Dune's [Get] Execution Status endpoint
    """

    execution_id: str
    query_id: int
    state: ExecutionState
    times: TimeData

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
        return cls(
            execution_id=data["execution_id"],
            query_id=int(data["query_id"]),
            state=ExecutionState(data["state"]),
            times=TimeData.from_dict(data),  # Sending the entire data dict
        )


@dataclass
class ResultMetadata:
    """
    Representation of Dune's Result Metadata from [Get] Query Results endpoint
    """

    column_names: list[str]
    result_set_bytes: int
    total_row_count: int

    @classmethod
    def from_dict(cls, data: dict[str, int | list[str]]) -> ResultMetadata:
        """
        Sample input.
        {
            "column_names": [
                "ct",
                "TableName"
            ],
            "result_set_bytes": 194,
            "total_row_count": 8
        }
        """
        assert isinstance(data["column_names"], list)
        assert isinstance(data["result_set_bytes"], int)
        assert isinstance(data["total_row_count"], int)
        return cls(
            column_names=data["column_names"],
            result_set_bytes=int(data["result_set_bytes"]),
            total_row_count=int(data["total_row_count"]),
        )


RowData = list[dict[str, str]]
MetaData = dict[str, Union[int, list[str]]]


@dataclass
class ExecutionResult:
    """Representation of `result` field of a Dune ResultsResponse"""

    rows: list[DuneRecord]
    metadata: ResultMetadata

    @classmethod
    def from_dict(cls, data: dict[str, RowData | MetaData]) -> ExecutionResult:
        """
        Sample Value:
        {
            "rows": [
                {
                    "TableName": "eth_blocks",
                    "ct": 6296
                },
                {
                    "TableName": "eth_traces",
                    "ct": 4474223
                }
            ],
            "metadata": {
                "column_names": [
                    "ct",
                    "TableName"
                ],
                "result_set_bytes": 194,
                "total_row_count": 8
            }
        }
        """
        assert isinstance(data["rows"], list)
        assert isinstance(data["metadata"], dict)
        return cls(
            rows=data["rows"],
            metadata=ResultMetadata.from_dict(data["metadata"]),
        )


ResultData = dict[str, Union[RowData, MetaData]]


@dataclass
class ResultsResponse:
    """
    Representation of Response from Dune's [Get] Query Results endpoint
    """

    execution_id: str
    query_id: int
    state: ExecutionState
    times: TimeData
    result: ExecutionResult

    @classmethod
    def from_dict(cls, data: dict[str, str | int | ResultData]) -> ResultsResponse:
        """
        Sample input.
        {
            "execution_id": "01GBM4W2N0NMCGPZYW8AYK4YF1",
            "query_id": 980708,
            "state": "QUERY_STATE_COMPLETED",
            "submitted_at": "2022-08-29T06:33:24.913138Z",
            "expires_at": "2024-08-28T06:36:41.58847Z",
            "execution_started_at": "2022-08-29T06:33:24.916543Z",
            "execution_ended_at": "2022-08-29T06:36:41.588467Z",
            "result": {
                "rows": [
                    {
                        "TableName": "eth_blocks",
                        "ct": 6296
                    },
                    {
                        "TableName": "eth_traces",
                        "ct": 4474223
                    }
                ],
                "metadata": {
                    "column_names": [
                        "ct",
                        "TableName"
                    ],
                    "result_set_bytes": 194,
                    "total_row_count": 8
                }
            }
        }
        """
        assert isinstance(data["execution_id"], str)
        assert isinstance(data["query_id"], int)
        assert isinstance(data["state"], str)
        assert isinstance(data["result"], dict)
        return cls(
            execution_id=data["execution_id"],
            query_id=int(data["query_id"]),
            state=ExecutionState(data["state"]),
            times=TimeData.from_dict(data),
            result=ExecutionResult.from_dict(data["result"]),
        )


class DuneClient:
    """
    An interface for Dune API with a few convenience methods
    combining the use of endpoints (e.g. refresh)
    """

    def __init__(self, api_key: str):
        self.token = api_key

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

    def get_result(self, job_id: str) -> ResultsResponse:
        """GET results from Dune API for `job_id` (aka `execution_id`)"""
        raw_response = requests.get(
            url=f"{BASE_URL}/execution/{job_id}/results",
            headers={"x-dune-api-key": self.token},
        )
        # TODO - log raw_response
        return ResultsResponse.from_dict(raw_response.json())

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

        return self.get_result(job_id).result.rows
