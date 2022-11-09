import os
from pathlib import Path

TEST_CONFIG_PATH = Path(__file__).parent / Path("data")


def filepath(name: str) -> str:
    return os.path.join(TEST_CONFIG_PATH, name)
