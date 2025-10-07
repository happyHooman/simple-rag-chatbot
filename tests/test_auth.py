"""Tests for authentication functionality."""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestAuthentication:
    """Test authentication on protected endpoints."""
    
    def test_health_check_no_auth_required(self):
        """Test health check works without authentication."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "overall_status" in response.json()
    
    def test_protected_endpoint_without_token(self):
        """Test protected endpoint without token returns 401."""
        response = client.post(
            "/ask-question",
            json={"user_question": "How do I reset my password?"}
        )
        assert response.status_code == 401
        assert "error" in response.json() or "detail" in response.json()
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test protected endpoint with invalid token returns 401."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post(
            "/ask-question",
            json={"user_question": "How do I reset my password?"},
            headers=headers
        )
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self):
        """Test protected endpoint with valid token succeeds."""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post(
            "/ask-question",
            json={"user_question": "How do I reset my password?"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "source" in data
        assert "answer" in data
    
    def test_generate_embeddings_requires_auth(self):
        """Test generate-embeddings requires authentication."""
        response = client.post("/generate-embeddings")
        assert response.status_code == 401
    
    def test_generate_embeddings_with_valid_token(self):
        """Test generate-embeddings works with valid token."""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post("/generate-embeddings", headers=headers)
        assert response.status_code == 200
    
    def test_update_embeddings_requires_auth(self):
        """Test update-embeddings requires authentication."""
        response = client.post("/update-embeddings")
        assert response.status_code == 401
