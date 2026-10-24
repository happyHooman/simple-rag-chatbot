import subprocess

import pytest

# Needs Docker and a real .env.
pytestmark = pytest.mark.live


class TestDatabaseReadiness:
    """Test database readiness for deployment."""
    
    def test_docker_available(self):
        """Test that Docker is available and running."""
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, "Docker is not available or not running"
    
    def test_docker_compose_available(self):
        """Test that Docker Compose is available."""
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, "Docker Compose is not available"
    
    def test_docker_compose_file_valid(self):
        """Test that docker-compose.yml is valid."""
        result = subprocess.run(
            ["docker", "compose", "config"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, f"docker-compose.yml is invalid: {result.stderr}"
    
    def test_database_connection_string_valid(self):
        """Test that database connection string is valid."""
        from app.config import settings
        
        assert hasattr(settings, 'DATABASE_URL'), "DATABASE_URL not configured"
        assert settings.DATABASE_URL is not None, "DATABASE_URL is None"
        assert settings.DATABASE_URL.startswith("postgresql://"), "DATABASE_URL must be a PostgreSQL URL"
