"""Tests for AI Router functionality."""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# Test configuration
VALID_TOKEN = "test_token"
HEADERS = {"Authorization": f"Bearer {VALID_TOKEN}"}

# These check the real LLM classifier, so they need an OpenAI key.
pytestmark = pytest.mark.live


class TestAIRouter:
    """Test AI Router classification and routing."""
    
    def test_it_question_password_reset(self):
        """Test IT question about password reset."""
        response = client.post(
            "/ask-question",
            json={"user_question": "How do I reset my password?"},
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source"] in ["local", "openai"], "IT question should route to local or openai"
    
    def test_it_question_technical_support(self):
        """Test IT question about technical issues."""
        response = client.post(
            "/ask-question",
            json={"user_question": "My computer is running slowly, what should I do?"},
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source"] in ["local", "openai"], "IT question should route to local or openai"
    
    def test_it_question_system_access(self):
        """Test IT question about system access."""
        response = client.post(
            "/ask-question",
            json={"user_question": "How do I access the company database?"},
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source"] in ["local", "openai"], "IT question should route to local or openai"
    
    def test_non_it_question_hr_policy(self):
        """Test non-IT question about HR policy."""
        response = client.post(
            "/ask-question",
            json={"user_question": "What is the company's vacation policy?"},
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "compliance", "Non-IT question should route to compliance"
        assert "not really what I was trained for" in data["answer"]
    
    def test_non_it_question_legal(self):
        """Test non-IT question about legal/compliance."""
        response = client.post(
            "/ask-question",
            json={"user_question": "What are the legal requirements for data retention?"},
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "compliance", "Non-IT question should route to compliance"
    
    def test_non_it_question_business_process(self):
        """Test non-IT question about business process."""
        response = client.post(
            "/ask-question",
            json={"user_question": "What is the process for submitting expense reports?"},
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "compliance", "Non-IT question should route to compliance"
        assert data["matched_question"] == "N/A"
    
    def test_compliance_response_format(self):
        """Test that compliance response has correct format."""
        response = client.post(
            "/ask-question",
            json={"user_question": "What's the weather like today?"},
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "compliance"
        assert data["matched_question"] == "N/A"
        assert "answer" in data
