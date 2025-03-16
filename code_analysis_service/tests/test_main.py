import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_start_analysis():
    with patch('app.tasks.clone_repository.delay') as mock_task:
        mock_task.return_value.id = "test_job_id"
        response = client.post(
            "/analyze/start",
            json={"repo_url": "https://github.com/example/repo"}
        )
        assert response.status_code == 200
        assert "job_id" in response.json()
        assert response.json()["job_id"] == "test_job_id"

def test_analyze_function():
    with patch('app.code_analyzer.analyze_function') as mock_analyze:
        mock_analyze.return_value = ["Add type hints", "Add docstring"]
        response = client.post(
            "/analyze/function",
            json={
                "job_id": "test_job_id",
                "function_name": "module.function"
            }
        )
        assert response.status_code == 200
        assert "suggestions" in response.json()
        assert len(response.json()["suggestions"]) == 2

def test_analyze_function_invalid_input():
    response = client.post(
        "/analyze/function",
        json={"invalid_key": "invalid_value"}
    )
    assert response.status_code == 422

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"} 