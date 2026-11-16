import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add docker-app directory to sys.path so app can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "docker-app"))

from app import app as flask_app  # noqa: E402


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_home_json(client):
    response = client.get("/?format=json")
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "environment" in data
    assert data["message"] == "Hello from a containerized Flask app!"


def test_home_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello, World!" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "flask-demo"


def test_init_db_mocked(client):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur

    with patch("app.get_conn", return_value=mock_conn):
        response = client.get("/init")
        assert response.status_code == 200
        assert response.data == b"database initialized"
        assert mock_cur.execute.called
        assert mock_conn.commit.called


def test_count_mocked(client):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = [42]
    mock_conn.cursor.return_value = mock_cur

    with patch("app.get_conn", return_value=mock_conn):
        response = client.get("/count")
        assert response.status_code == 200
        data = response.get_json()
        assert data["total_visits"] == 42


def test_student_api_post_and_get(client):
    with patch("os.path.exists", return_value=True):
        # Post student
        post_res = client.post(
            "/api/students",
            data=json.dumps({"name": "Alice", "age": 20}),
            content_type="application/json",
        )
        assert post_res.status_code == 201
        res_data = post_res.get_json()
        assert res_data["message"] == "Student saved successfully"

        # Post invalid student
        bad_res = client.post(
            "/api/students",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert bad_res.status_code == 400
