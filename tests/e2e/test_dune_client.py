import os
import time
import unittest

import dotenv
from duneapi.types import DuneRecord

from src.dune_client import (
    DuneClient,
    ExecutionResponse,
    ExecutionStatusResponse,
    ExecutionState,
)
from src.query_monitor.factory import load_from_config


class MyTestCase(unittest.TestCase):
    def test_execute(self):
        dotenv.load_dotenv()
        dune = DuneClient(api_key=os.environ["DUNE_API_KEY"])
        query = load_from_config("./tests/data/v2-test-data.yaml")
        execution_response = dune.execute(query)
        self.assertIsInstance(execution_response, ExecutionResponse)
        job_id = execution_response.execution_id
        status = dune.get_status(job_id)
        self.assertIsInstance(status, ExecutionStatusResponse)
        while dune.get_status(job_id).state != ExecutionState.COMPLETED:
            time.sleep(1)
        results = dune.get_results(job_id)
        self.assertGreater(len(results), 0)


if __name__ == "__main__":
    unittest.main()
