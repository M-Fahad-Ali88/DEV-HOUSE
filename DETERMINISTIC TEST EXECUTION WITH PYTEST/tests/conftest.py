import sys
from pathlib import Path

# Add the project root to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest


@pytest.fixture(scope="function")
def sample_user():
    print("\n[SETUP] Function Fixture")

    user = {
        "name": "Ali",
        "age": 22,
        "email": "ali@gmail.com"
    }

    yield user

    print("[TEARDOWN] Function Fixture")


@pytest.fixture(scope="module")
def database():
    print("\nConnecting Database...")

    db = {
        "status": "Connected"
    }

    yield db

    print("Closing Database...")


@pytest.fixture(scope="session")
def app_config():
    print("\nLoading Application Configuration")

    config = {
        "version": "1.0",
        "environment": "Testing"
    }

    yield config

    print("Application Configuration Released")