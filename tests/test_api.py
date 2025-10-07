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
    """Test embeddings management endpoints (now async with Celery)."""
    
    def test_generate_embeddings_dispatch(self):
        """Test embeddings generation dispatches a task."""
        response = client.post("/generate-embeddings", headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "processing"
        assert "task_id" in data
        assert "message" in data
        # Task ID should be a valid UUID-like string
        assert len(data["task_id"]) > 0
    
    def test_update_embeddings_dispatch(self):
        """Test embeddings update dispatches a task."""
        response = client.post("/update-embeddings", headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "processing"
        assert "task_id" in data
        assert "message" in data


class TestTaskStatusEndpoint:
    """Test task status endpoint."""
    
    def test_task_status_endpoint_exists(self):
        """Test that task status endpoint is accessible."""
        # Use a fake task ID to test endpoint existence
        fake_task_id = "12345678-1234-1234-1234-123456789012"
        response = client.get(f"/tasks/{fake_task_id}", headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "state" in data
        assert data["task_id"] == fake_task_id
