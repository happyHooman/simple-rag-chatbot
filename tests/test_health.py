"""Tests for health check functionality."""
from unittest.mock import patch, MagicMock

from app.api.helpers.health_check import (
    check_docker_container,
    check_database_connection,
    check_embeddings_status,
    get_comprehensive_health
)

# Status constants for better maintainability
class HealthStatus:
    # Overall status
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    
    # Docker status
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    
    # Database status
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    
    # Embeddings status
    LOADED = "loaded"
    EMPTY = "empty"


class TestDockerContainerCheck:
    """Docker container health check."""
    
    @patch('subprocess.run')
    def test_docker_container_running(self, mock_run):
        """Test when Docker container is running."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Up 2 hours"
        
        result = check_docker_container()
        
        assert result["status"] == HealthStatus.RUNNING
        assert result["running"] is True
        assert "Up" in result["container_status"]
    
    @patch('subprocess.run')
    def test_docker_container_not_running(self, mock_run):
        """Test when Docker container is not running."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        
        result = check_docker_container()
        
        assert result["status"] == HealthStatus.STOPPED
        assert result["running"] is False
    
    @patch('subprocess.run')
    def test_docker_command_failed(self, mock_run):
        """Test when Docker command fails."""
        mock_run.side_effect = FileNotFoundError("Docker not found")
        
        result = check_docker_container()
        
        assert result["status"] == HealthStatus.ERROR
        assert result["running"] is False


class TestDatabaseConnectionCheck:
    """Test database connection health check."""
    
    @patch('psycopg2.connect')
    def test_database_connection_success(self, mock_connect):
        """Test successful database connection."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(1,), (1,)]  # Basic query and vector extension
        mock_connect.return_value = mock_conn
        
        result = check_database_connection()
        
        assert result["status"] == HealthStatus.CONNECTED
        assert result["connection"] == "successful"
        assert result["pgvector_available"] is True
    
    @patch('psycopg2.connect')
    def test_database_connection_failed(self, mock_connect):
        """Test failed database connection."""
        mock_connect.side_effect = Exception("Connection failed")
        
        result = check_database_connection()
        
        assert result["status"] == HealthStatus.ERROR
        assert result["connection"] == "error"


class TestEmbeddingsStatusCheck:
    """Test embeddings status check."""
    
    @patch('app.api.helpers.health_check.get_embeddings_count')
    def test_embeddings_with_data(self, mock_count):
        """Test when embeddings exist."""
        mock_count.return_value = 2
        result = check_embeddings_status()
        
        assert result["status"] == HealthStatus.LOADED
        assert result["embeddings_count"] == 2
        assert result["has_embeddings"] is True
    
    @patch('app.api.helpers.health_check.get_embeddings_count')
    def test_embeddings_empty(self, mock_count):
        """Test when no embeddings exist."""
        mock_count.return_value = 0
        result = check_embeddings_status()
        
        assert result["status"] == HealthStatus.EMPTY
        assert result["embeddings_count"] == 0
        assert result["has_embeddings"] is False


class TestComprehensiveHealth:
    """Test comprehensive health check."""
    
    @patch('app.api.helpers.health_check.check_docker_container')
    @patch('app.api.helpers.health_check.check_database_connection')
    @patch('app.api.helpers.health_check.check_embeddings_status')
    def test_all_services_healthy(self, mock_embeddings, mock_db, mock_docker):
        """Test when all services are healthy."""
        mock_docker.return_value = {"status": HealthStatus.RUNNING, "running": True}
        mock_db.return_value = {"status": HealthStatus.CONNECTED, "connection": "successful"}
        mock_embeddings.return_value = {"status": HealthStatus.LOADED, "has_embeddings": True}
        
        result = get_comprehensive_health()
        
        assert result["overall_status"] == HealthStatus.OPERATIONAL
        assert result["summary"]["docker_running"] is True
        assert result["summary"]["database_connected"] is True
        assert result["summary"]["embeddings_ready"] is True
    
    @patch('app.api.helpers.health_check.check_docker_container')
    @patch('app.api.helpers.health_check.check_database_connection')
    @patch('app.api.helpers.health_check.check_embeddings_status')
    def test_some_services_unhealthy(self, mock_embeddings, mock_db, mock_docker):
        """Test when some services are unhealthy."""
        mock_docker.return_value = {"status": HealthStatus.STOPPED, "running": False}
        mock_db.return_value = {"status": HealthStatus.CONNECTED, "connection": "successful"}
        mock_embeddings.return_value = {"status": HealthStatus.LOADED, "has_embeddings": True}
        
        result = get_comprehensive_health()
        
        assert result["overall_status"] == HealthStatus.DEGRADED
        assert result["summary"]["docker_running"] is False
        assert result["summary"]["database_connected"] is True
        assert result["summary"]["embeddings_ready"] is True
