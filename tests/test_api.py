"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# Test configuration
VALID_TOKEN = "test_token"
HEADERS = {"Authorization": f"Bearer {VALID_TOKEN}"}


class TestBasicEndpoints:
    """Test basic API endpoints."""
    
    def test_health_endpoint(self):
        """Test health endpoint (public - no auth required)."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        assert "services" in data
        assert "summary" in data


class TestAskQuestionEndpoint:
    """Test ask question endpoint."""
    
    def test_ask_question_success(self):
        """Test successful ask question request."""
        payload = {"user_question": "How do I reset my password?"}
        response = client.post("/ask-question", json=payload, headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert "source" in data
        assert "matched_question" in data
        assert "answer" in data
        assert data["source"] in ["local", "openai", "compliance"]
    
    def test_ask_question_invalid_payload(self):
        """Test ask question with invalid payload."""
        payload = {"invalid_field": "test"}
        response = client.post("/ask-question", json=payload, headers=HEADERS)
        
        assert response.status_code == 422


class TestEmbeddingsEndpoints:
    """Test embeddings management endpoints."""
    
    def test_generate_embeddings_success(self):
        """Test successful embeddings generation (requires database)."""
        response = client.post("/generate-embeddings", headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "count" in data
        assert data["count"] > 0
    
    def test_update_embeddings_success(self):
        """Test successful embeddings update (requires database)."""
        response = client.post("/update-embeddings", headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "changes" in data
        assert "added" in data["changes"]
        assert "updated" in data["changes"]
        assert "removed" in data["changes"]
