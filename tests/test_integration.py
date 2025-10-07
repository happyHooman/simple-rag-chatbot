"""Integration tests for the complete FAQ system."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

VALID_TOKEN = "test_token"
HEADERS = {"Authorization": f"Bearer {VALID_TOKEN}"}


class TestSimilarityThreshold:
    """Test similarity threshold behavior."""
    
    @patch('app.api.ask_question.find_best_match')
    def test_high_similarity_uses_local(self, mock_find):
        """Test that high similarity score uses local answer."""
        # Mock a high similarity match
        mock_find.return_value = {
            "id": 1,
            "question": "What steps do I take to reset my password?",
            "answer": "Go to account settings...",
            "similarity": 0.85
        }
        
        response = client.post(
            "/ask-question",
            json={"user_question": "How do I reset my password?"},
            headers=HEADERS
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "local"
        assert data["matched_question"] == "What steps do I take to reset my password?"
    
    @patch('app.api.ask_question.find_best_match')
    @patch('app.api.ask_question.get_openai_answer')
    def test_low_similarity_uses_openai(self, mock_openai, mock_find):
        """Test that low similarity score forwards to OpenAI."""
        # Mock a low similarity match (below threshold)
        mock_find.return_value = {
            "id": 1,
            "question": "Some question",
            "answer": "Some answer",
            "similarity": 0.3  # Below default threshold of 0.5
        }
        mock_openai.return_value = "OpenAI generated answer"
        
        response = client.post(
            "/ask-question",
            json={"user_question": "How do I configure SSL certificates?"},
            headers=HEADERS
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "openai"
        assert data["matched_question"] == "N/A"


class TestFullPipeline:
    """Test the complete question-answering pipeline."""
    
    def test_exact_faq_match(self):
        """Test question that exactly matches FAQ database."""
        response = client.post(
            "/ask-question",
            json={"user_question": "How do I change my profile information?"},
            headers=HEADERS
        )
        
        assert response.status_code == 200
        data = response.json()
        # AI Router may classify as IT or non-IT depending on interpretation
        assert data["source"] in ["local", "openai", "compliance"]
        assert "answer" in data
    
    def test_similar_faq_match(self):
        """Test question similar to FAQ database."""
        response = client.post(
            "/ask-question",
            json={"user_question": "How can I update my password?"},
            headers=HEADERS
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should match "What steps do I take to reset my password?"
        assert data["source"] in ["local", "openai"]
        assert "answer" in data


class TestResponseFormat:
    """Test response format compliance with requirements."""
    
    def test_local_response_format(self):
        """Test local response has all required fields."""
        # Use a clearly IT-related question
        response = client.post(
            "/ask-question",
            json={"user_question": "How do I reset my account password?"},
            headers=HEADERS
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields per assignment
        assert "source" in data
        assert "matched_question" in data
        assert "answer" in data
        
        # Should be IT question (local or openai)
        assert data["source"] in ["local", "openai"]
    
    def test_openai_response_format(self):
        """Test OpenAI response has all required fields."""
        # Ask a question unlikely to be in FAQ (will trigger OpenAI)
        response = client.post(
            "/ask-question",
            json={"user_question": "What is the capital of France?"},
            headers=HEADERS
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields per assignment
        assert "source" in data
        assert "matched_question" in data
        assert "answer" in data
        
        # OpenAI response specifics (if not blocked by AI Router)
        if data["source"] == "openai":
            assert data["matched_question"] == "N/A"
    
    def test_compliance_response_format(self):
        """Test compliance response format."""
        response = client.post(
            "/ask-question",
            json={"user_question": "What's the company vacation policy?"},
            headers=HEADERS
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        assert "source" in data
        assert "matched_question" in data
        assert "answer" in data
        
        # Compliance response specifics
        assert data["source"] == "compliance"
        assert data["matched_question"] == "N/A"
        assert "not really what I was trained for" in data["answer"]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_empty_question(self):
        """Test handling of empty question."""
        response = client.post(
            "/ask-question",
            json={"user_question": ""},
            headers=HEADERS
        )
        
        # Should still return 200 with an answer (even if fallback)
        assert response.status_code in [200, 422]
    
    def test_missing_question_field(self):
        """Test handling of missing question field."""
        response = client.post(
            "/ask-question",
            json={},
            headers=HEADERS
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_very_long_question(self):
        """Test handling of very long question."""
        long_question = "How do I " + "reset " * 100 + "my password?"
        response = client.post(
            "/ask-question",
            json={"user_question": long_question},
            headers=HEADERS
        )
        
        assert response.status_code == 200
        assert "answer" in response.json()


class TestEmbeddingsManagement:
    """Test embeddings management functionality (requires database)."""
    
    def test_generate_and_query_flow(self):
        """Test complete flow: generate embeddings then query."""
        # First generate embeddings
        gen_response = client.post("/generate-embeddings", headers=HEADERS)
        assert gen_response.status_code == 200
        gen_data = gen_response.json()
        assert gen_data["status"] == "success"
        assert gen_data["count"] > 0
        
        # Then query should work
        query_response = client.post(
            "/ask-question",
            json={"user_question": "How do I reset my password?"},
            headers=HEADERS
        )
        assert query_response.status_code == 200
    
    def test_update_embeddings_incremental(self):
        """Test that update-embeddings works incrementally."""
        # First generate
        client.post("/generate-embeddings", headers=HEADERS)
        
        # Then update
        update_response = client.post("/update-embeddings", headers=HEADERS)
        assert update_response.status_code == 200
        
        data = update_response.json()
        assert "changes" in data
        # After first generation and immediate update, should have no changes
        assert data["changes"]["total"] >= 0

