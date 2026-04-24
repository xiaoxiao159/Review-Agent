from datetime import datetime, timedelta
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_header(client):
    login = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@123456"})
    token = login.json()["access_token"]
    return {"authorization": f"Bearer {token}"}
