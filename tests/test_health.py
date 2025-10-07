"""Tests for health check functionality."""
from unittest.mock import patch, MagicMock

from app.api.helpers.health_check import (
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
    
    @patch('app.api.helpers.health_check.check_celery_worker')
    @patch('app.api.helpers.health_check.check_redis_connection')
    @patch('app.api.helpers.health_check.check_database_connection')
    @patch('app.api.helpers.health_check.check_embeddings_status')
    def test_all_services_healthy(self, mock_embeddings, mock_db, mock_redis, mock_celery):
        """Test when all services are healthy."""
        mock_db.return_value = {"status": HealthStatus.CONNECTED, "connection": "successful"}
        mock_embeddings.return_value = {"status": HealthStatus.LOADED, "has_embeddings": True}
        mock_redis.return_value = {"status": HealthStatus.CONNECTED, "version": "7.0.0"}
        mock_celery.return_value = {"status": HealthStatus.RUNNING, "worker_count": 1}
        
        result = get_comprehensive_health()
        
        assert result["overall_status"] == HealthStatus.OPERATIONAL
        assert result["summary"]["database_connected"] is True
        assert result["summary"]["redis_connected"] is True
        assert result["summary"]["celery_workers_active"] is True
        assert result["summary"]["embeddings_ready"] is True
    
    @patch('app.api.helpers.health_check.check_celery_worker')
    @patch('app.api.helpers.health_check.check_redis_connection')
    @patch('app.api.helpers.health_check.check_database_connection')
    @patch('app.api.helpers.health_check.check_embeddings_status')
    def test_some_services_unhealthy(self, mock_embeddings, mock_db, mock_redis, mock_celery):
        """Test when some services are unhealthy."""
        mock_db.return_value = {"status": HealthStatus.CONNECTED, "connection": "successful"}
        mock_embeddings.return_value = {"status": HealthStatus.LOADED, "has_embeddings": True}
        mock_redis.return_value = {"status": HealthStatus.DISCONNECTED, "error": "Connection refused"}
        mock_celery.return_value = {"status": HealthStatus.RUNNING, "worker_count": 1}
        
        result = get_comprehensive_health()
        
        assert result["overall_status"] == HealthStatus.DEGRADED
        assert result["summary"]["database_connected"] is True
        assert result["summary"]["redis_connected"] is False
        assert result["summary"]["embeddings_ready"] is True
