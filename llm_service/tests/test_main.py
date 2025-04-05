import pytest
from fastapi.testclient import TestClient
from llm_service.app.main import app

client = TestClient(app)

def test_analyze_endpoint():
    response = client.post(
        "/analyze",
        json={"function_code": "def add(a, b): return a + b"}
    )
    assert response.status_code == 200
    assert "suggestions" in response.json()
    assert isinstance(response.json()["suggestions"], list)

def test_analyze_endpoint_invalid_input():
    response = client.post(
        "/analyze",
        json={"invalid_key": "invalid_value"}
    )
    assert response.status_code == 422

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"} 