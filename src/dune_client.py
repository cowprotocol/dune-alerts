""""
Basic Dune Client Class responsible for refreshing Dune Queries
Framework built on Dune's API Documentation
https://duneanalytics.notion.site/API-Documentation-1b93d16e0fa941398e15047f643e003a
"""
from __future__ import annotations

import logging.config
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from json import JSONDecodeError
from typing import Union, Optional, Any

from dateutil.parser import parse
import requests
from duneapi.api import DuneAPI
from duneapi.types import DuneRecord
from requests import Response

from src.dune_interface import DuneInterface
from src.query_monitor.base import QueryBase

log = logging.getLogger(__name__)
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)

BASE_URL = "https://api.dune.com/api/v1"


class DuneError(Exception):
    """Possibilities seen so far
    {'error': 'invalid API Key'}
    {'error': 'Query not found'}
    {'error': 'An internal error occured'}
    {'error': 'The requested execution ID (ID: Wonky Job ID) is invalid.'}
    """

    def __init__(self, data: dict[str, str], response_class: str):
        super().__init__(f"Can't build {response_class} from {data}")


class ExecutionState(Enum):
    """
    Enum for possible values of Query Execution
    """

    COMPLETED = "QUERY_STATE_COMPLETED"
    EXECUTING = "QUERY_STATE_EXECUTING"
    PENDING = "QUERY_STATE_PENDING"


@dataclass
class ExecutionResponse:
    """
    Representation of Response from Dune's [Post] Execute Query ID endpoint
    """

    execution_id: str
    state: ExecutionState

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> ExecutionResponse:
        """Constructor from dictionary. See unit test for sample input."""
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TimeData:
        """Constructor from dictionary. See unit test for sample input."""
        end = data.get("execution_ended_at", None)
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
        """Constructor from dictionary. See unit test for sample input."""
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
        """Constructor from dictionary. See unit test for sample input."""
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
        """Constructor from dictionary. See unit test for sample input."""
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
        """Constructor from dictionary. See unit test for sample input."""
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


class DuneClient(DuneInterface):
    """
    An interface for Dune API with a few convenience methods
    combining the use of endpoints (e.g. refresh)
    """

    def __init__(self, api_key: str):
        self.token = api_key

    @staticmethod
    def _handle_response(
        response: Response,
    ) -> Any:
        try:
            # Some responses can be decoded and converted to DuneErrors
            return response.json()
        except JSONDecodeError as err:
            # Others can't. Only raise HTTP error for not decodable errors
            response.raise_for_status()
            raise ValueError("Unreachable since previous line raises") from err

    def _get(self, url: str) -> Any:
        response = requests.get(url, headers={"x-dune-api-key": self.token})
        return self._handle_response(response)

    def _post(self, url: str, params: Any) -> Any:
        response = requests.post(
            url=url, params=params, headers={"x-dune-api-key": self.token}
        )
        return self._handle_response(response)

    def execute(self, query: QueryBase) -> ExecutionResponse:
        """Post's to Dune API for execute `query`"""
        response_json = self._post(
            url=f"{BASE_URL}/query/{query.query_id}/execute",
            params={
                "query_parameters": {
                    param.key: param.value for param in query.parameters()
                }
            },
        )
        log.debug(f"execute response {response_json}")
        try:
            return ExecutionResponse.from_dict(response_json)
        except KeyError as err:
            raise DuneError(response_json, "ExecutionResponse") from err

    def get_status(self, job_id: str) -> ExecutionStatusResponse:
        """GET status from Dune API for `job_id` (aka `execution_id`)"""
        response_json = self._get(
            url=f"{BASE_URL}/execution/{job_id}/status",
        )
        log.debug(f"get_status response {response_json}")
        try:
            return ExecutionStatusResponse.from_dict(response_json)
        except KeyError as err:
            raise DuneError(response_json, "ExecutionStatusResponse") from err

    def get_result(self, job_id: str) -> ResultsResponse:
        """GET results from Dune API for `job_id` (aka `execution_id`)"""
        response_json = self._get(url=f"{BASE_URL}/execution/{job_id}/results")
        log.debug(f"get_result response {response_json}")
        try:
            return ResultsResponse.from_dict(response_json)
        except KeyError as err:
            raise DuneError(response_json, "ResultsResponse") from err

    def refresh(self, query: QueryBase) -> list[DuneRecord]:
        """
        Executes a Dune query, waits till query execution completes,
        fetches and returns the results.
        *Sleeps 3 seconds between each request*.
        """
        job_id = self.execute(query).execution_id
        while self.get_status(job_id).state != ExecutionState.COMPLETED:
            log.info(f"waiting for query execution {job_id} to complete")
            # TODO - use a better model for status pings.
            time.sleep(5)

        return self.get_result(job_id).result.rows


class LegacyDuneClient(DuneInterface):
    """Implementation of DuneInterface using the "legacy" (browser emulator) duneapi"""

    def __init__(self, dune: DuneAPI):
        self.dune = dune

    def refresh(self, query: QueryBase) -> list[DuneRecord]:
        """Executes dune query by ID, and fetches the results by job ID returned"""
        job_id = self.dune.execute(query.query_id, query.parameters())
        return self.dune.get_results(job_id)
