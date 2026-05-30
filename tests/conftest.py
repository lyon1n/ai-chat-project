import os
import tempfile

import pytest
from fastapi.testclient import TestClient

_TEST_ROOT = tempfile.mkdtemp(prefix="ai-chat-tests-")

os.environ["USE_SQLITE"] = "true"
os.environ["SQLITE_PATH"] = os.path.join(_TEST_ROOT, "chat.db")
os.environ["CHROMA_PATH"] = os.path.join(_TEST_ROOT, "chroma")
os.environ["UPLOAD_DIR"] = os.path.join(_TEST_ROOT, "uploads")
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["DEEPSEEK_API_KEY"] = "test-key"

from backend.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    def _auth_headers(username: str):
        response = client.post(
            "/register",
            json={"username": username, "password": "secret123"},
        )
        assert response.status_code == 200
        response = client.post(
            "/login",
            json={"username": username, "password": "secret123"},
        )
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json()['token']}"}

    return _auth_headers
