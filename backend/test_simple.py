import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Simple test to verify the API is working"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"