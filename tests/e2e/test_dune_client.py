import copy
import os
import time
import unittest

import dotenv
from requests import JSONDecodeError

from src.dune_client import (
    DuneClient,
    ExecutionResponse,
    ExecutionStatusResponse,
    ExecutionState,
    DuneError,
)
from src.query_monitor.factory import load_from_config


class TestDuneClient(unittest.TestCase):
    def setUp(self) -> None:
        self.query = load_from_config("./tests/data/v2-test-data.yaml")
        dotenv.load_dotenv()
        self.valid_api_key = os.environ["DUNE_API_KEY"]

    def test_endpoints(self):
        dune = DuneClient(self.valid_api_key)
        # POST Execution
        execution_response = dune.execute(self.query)
        self.assertIsInstance(execution_response, ExecutionResponse)

        # GET Execution Status
        job_id = execution_response.execution_id
        status = dune.get_status(job_id)
        self.assertIsInstance(status, ExecutionStatusResponse)

        # GET ExecutionResults
        while dune.get_status(job_id).state != ExecutionState.COMPLETED:
            time.sleep(1)
        results = dune.get_result(job_id).result.rows
        self.assertGreater(len(results), 0)

    def test_cancel_execution(self):
        dune = DuneClient(self.valid_api_key)
        query = load_from_config("./tests/data/v2-long-running-query.yaml")
        execution_response = dune.execute(query)
        # POST Cancellation
        success = dune.cancel_execution(execution_response.execution_id)
        self.assertTrue(success)

    def test_invalid_api_key_error(self):
        dune = DuneClient(api_key="Invalid Key")
        with self.assertRaises(DuneError) as err:
            dune.execute(self.query)
        self.assertEqual(
            str(err.exception),
            "Can't build ExecutionResponse from {'error': 'invalid API Key'}",
        )
        with self.assertRaises(DuneError) as err:
            dune.get_status("wonky job_id")
        self.assertEqual(
            str(err.exception),
            "Can't build ExecutionStatusResponse from {'error': 'invalid API Key'}",
        )
        with self.assertRaises(DuneError) as err:
            dune.get_result("wonky job_id")
        self.assertEqual(
            str(err.exception),
            "Can't build ResultsResponse from {'error': 'invalid API Key'}",
        )

    def test_query_not_found_error(self):
        dune = DuneClient(self.valid_api_key)
        query = copy.copy(self.query)
        query.query.query_id = 99999999  # Invalid Query Id.

        with self.assertRaises(DuneError) as err:
            dune.execute(query)
        self.assertEqual(
            str(err.exception),
            "Can't build ExecutionResponse from {'error': 'Query not found'}",
        )

    def test_internal_error(self):
        dune = DuneClient(self.valid_api_key)
        query = copy.copy(self.query)
        # This query ID is too large!
        query.query.query_id = 9999999999999

        with self.assertRaises(DuneError) as err:
            dune.execute(query)
        self.assertEqual(
            str(err.exception),
            "Can't build ExecutionResponse from {'error': 'An internal error occured'}",
        )

    def test_invalid_job_id_error(self):
        dune = DuneClient(self.valid_api_key)

        with self.assertRaises(DuneError) as err:
            dune.get_status("Wonky Job ID")
        self.assertEqual(
            str(err.exception),
            "Can't build ExecutionStatusResponse from "
            "{'error': 'The requested execution ID (ID: Wonky Job ID) is invalid.'}",
        )


if __name__ == "__main__":
    unittest.main()
