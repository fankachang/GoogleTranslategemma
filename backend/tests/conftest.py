# pytest fixtures for backend tests
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
