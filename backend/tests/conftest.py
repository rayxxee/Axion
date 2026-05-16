"""Test fixtures for Axion backend."""

import pytest
from fastapi.testclient import TestClient

import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_article_text():
    """Demo article text for pipeline testing."""
    return (
        "KARACHI: The State Bank of Pakistan (SBP) has announced an increase "
        "in the policy rate by 200 basis points, bringing the key interest rate "
        "to 19.5%. The Monetary Policy Committee (MPC) cited persistent "
        "inflationary pressures and external sector vulnerabilities."
    )
