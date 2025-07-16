import pytest
import os
import tempfile
import json
from fastapi.testclient import TestClient
from app.main import create_app
from app.services.dependency_injection import container


@pytest.fixture
def temp_storage_file():
    """Create a temporary file for testing"""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    return temp_file.name


@pytest.fixture
def client(temp_storage_file):
    """Create a test client with temporary storage"""
    from app.infrastructure.repositories import JSONVLANRepository
    from app.services.vlan_service import VLANService
    
    # Reset the container
    container.reset()
    
    # Create test repository and service
    test_repository = JSONVLANRepository(temp_storage_file)
    test_service = VLANService(test_repository)
    
    # Override container with test instances
    container._vlan_repository = test_repository
    container._vlan_service = test_service
    
    # Create app
    app = create_app()
    
    with TestClient(app) as client:
        yield client
    
    # Cleanup
    container.reset()
    os.unlink(temp_storage_file)


class TestErrorHandling:
    def test_404_get_nonexistent_vlan(self, client):
        """Test 404 error for non-existent VLAN"""
        response = client.get("/api/v1/vlans/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "VLAN_NOT_FOUND"
        assert "message" in data
        assert data["details"]["vlan_id"] == 999
    
    def test_404_update_nonexistent_vlan(self, client):
        """Test 404 error when updating non-existent VLAN"""
        update_data = {"name": "Updated VLAN"}
        response = client.put("/api/v1/vlans/999", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "VLAN_NOT_FOUND"
        assert data["details"]["vlan_id"] == 999
    
    def test_404_delete_nonexistent_vlan(self, client):
        """Test 404 error when deleting non-existent VLAN"""
        response = client.delete("/api/v1/vlans/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "VLAN_NOT_FOUND"
        assert data["details"]["vlan_id"] == 999
    
    def test_409_duplicate_vlan_id(self, client):
        """Test 409 conflict error for duplicate VLAN ID"""
        vlan_data = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        # Create first VLAN
        response = client.post("/api/v1/vlans", json=vlan_data)
        assert response.status_code == 201
        
        # Try to create duplicate
        response = client.post("/api/v1/vlans", json=vlan_data)
        assert response.status_code == 409
        data = response.json()
        assert data["error"] == "VLAN_CONFLICT"
        assert data["details"]["vlan_id"] == 100
    
    def test_409_update_vlan_id_conflict(self, client):
        """Test 409 conflict when updating to existing VLAN ID"""
        # Create two VLANs
        vlan1 = {
            "name": "VLAN 1",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        vlan2 = {
            "name": "VLAN 2", 
            "vlan_id": 200,
            "subnet": "192.168.2.0/24",
            "gateway": "192.168.2.1",
            "status": "active"
        }
        
        client.post("/api/v1/vlans", json=vlan1)
        response = client.post("/api/v1/vlans", json=vlan2)
        created_vlan = response.json()
        
        # Try to update second VLAN to use first VLAN's ID
        response = client.put(f"/api/v1/vlans/{created_vlan['id']}", json={"vlan_id": 100})
        assert response.status_code == 409
        data = response.json()
        assert data["error"] == "VLAN_CONFLICT"
        assert data["details"]["vlan_id"] == 100
    
    def test_422_invalid_vlan_id_range(self, client):
        """Test 422 validation error for VLAN ID out of range"""
        invalid_vlan = {
            "name": "Test VLAN",
            "vlan_id": 5000,  # Out of valid range
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        response = client.post("/api/v1/vlans", json=invalid_vlan)
        assert response.status_code == 422
        data = response.json()
        assert "errors" in data["details"]
    
    def test_422_invalid_ip_address(self, client):
        """Test 422 validation error for invalid IP format"""
        invalid_vlan = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "invalid-ip",
            "status": "active"
        }
        
        response = client.post("/api/v1/vlans", json=invalid_vlan)
        assert response.status_code == 422
        data = response.json()
        assert "errors" in data["details"]
    
    def test_422_invalid_subnet_format(self, client):
        """Test 422 validation error for invalid subnet format"""
        invalid_vlan = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "invalid-subnet",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        response = client.post("/api/v1/vlans", json=invalid_vlan)
        assert response.status_code == 422
        data = response.json()
        assert "errors" in data["details"]
    
    def test_422_gateway_not_in_subnet(self, client):
        """Test 422 validation error for gateway not in subnet"""
        invalid_vlan = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "10.0.0.1",  # Not in subnet
            "status": "active"
        }
        
        response = client.post("/api/v1/vlans", json=invalid_vlan)
        assert response.status_code == 422
        data = response.json()
        assert "errors" in data["details"]
    
    def test_422_invalid_status(self, client):
        """Test 422 validation error for invalid status"""
        invalid_vlan = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "invalid-status"
        }
        
        response = client.post("/api/v1/vlans", json=invalid_vlan)
        assert response.status_code == 422
        data = response.json()
        assert "errors" in data["details"]
    
    def test_422_missing_required_fields(self, client):
        """Test 422 validation error for missing required fields"""
        incomplete_vlan = {
            "name": "Test VLAN"
            # Missing vlan_id, subnet, gateway, status
        }
        
        response = client.post("/api/v1/vlans", json=incomplete_vlan)
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "REQUEST_VALIDATION_ERROR"
        assert "errors" in data["details"]
    
    def test_422_name_too_long(self, client):
        """Test 422 validation error for name too long"""
        invalid_vlan = {
            "name": "x" * 101,  # Exceeds max length
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        response = client.post("/api/v1/vlans", json=invalid_vlan)
        assert response.status_code == 422
        data = response.json()
        assert "errors" in data["details"]
    
    def test_422_invalid_json_body(self, client):
        """Test 422 error for malformed JSON"""
        # Send invalid JSON
        response = client.post(
            "/api/v1/vlans",
            content="invalid json content",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error for unsupported HTTP method"""
        # PATCH is not supported on VLAN endpoints
        response = client.patch("/api/v1/vlans/1", json={"name": "test"})
        assert response.status_code == 405
    
    def test_500_internal_server_error_simulation(self, client):
        """Test 500 error handling by testing the exception handler directly"""
        import pytest
        from fastapi import Request
        from app.api.error_handlers import general_exception_handler
        
        # Create a mock request
        mock_request = Request({"type": "http", "method": "GET", "url": "http://test/api/v1/vlans"})
        
        # Create an unexpected exception (simulates database failure, network error, etc.)
        test_exception = RuntimeError("Database connection failed")
        
        # Test the general exception handler directly
        @pytest.mark.asyncio
        async def run_test():
            response = await general_exception_handler(mock_request, test_exception)
            
            # Check the response
            assert response.status_code == 500
            
            # Parse response content
            import json
            data = json.loads(response.body.decode())
            
            # Check the error response structure matches OpenAPI spec
            assert "error" in data
            assert "message" in data
            assert data["error"] == "INTERNAL_ERROR"
            assert data["message"] == "An internal server error occurred"
            
        # Run the async test
        import asyncio
        asyncio.run(run_test())
    
    def test_503_storage_unavailable_create(self, client):
        """Test 503 error when storage fails during VLAN creation"""
        from unittest.mock import patch
        from app.services.dependency_injection import container
        from app.domain.exceptions import StorageError
        
        # Get the repository instance
        repository = container.get_vlan_repository()
        
        # VLAN creation data
        vlan_data = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        # Mock the _save_data method to raise StorageError (simulates disk full, permission denied, etc.)
        with patch.object(repository, '_save_data', side_effect=StorageError("Failed to save data: Disk full")):
            response = client.post("/api/v1/vlans", json=vlan_data)
            
            assert response.status_code == 503
            data = response.json()
            
            # Check the error response structure matches OpenAPI spec
            assert "error" in data
            assert "message" in data
            assert data["error"] == "STORAGE_ERROR"
            assert data["message"] == "Storage system error occurred"
    
    def test_503_storage_unavailable_update(self, client):
        """Test 503 error when storage fails during VLAN update"""
        from unittest.mock import patch
        from app.services.dependency_injection import container
        from app.domain.exceptions import StorageError
        
        # Get the repository instance
        repository = container.get_vlan_repository()
        
        # First create a VLAN successfully
        vlan_data = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        response = client.post("/api/v1/vlans", json=vlan_data)
        assert response.status_code == 201
        created_vlan = response.json()
        
        # Then simulate storage failure during update
        update_data = {"name": "Updated VLAN"}
        with patch.object(repository, '_save_data', side_effect=StorageError("Failed to save data: I/O error")):
            response = client.put(f"/api/v1/vlans/{created_vlan['id']}", json=update_data)
            
            assert response.status_code == 503
            data = response.json()
            
            # Check the error response structure
            assert "error" in data
            assert "message" in data
            assert data["error"] == "STORAGE_ERROR"
            assert data["message"] == "Storage system error occurred"


class TestErrorResponseFormat:
    def test_error_response_structure_404(self, client):
        """Test that 404 errors have correct response structure"""
        response = client.get("/api/v1/vlans/999")
        
        assert response.status_code == 404
        data = response.json()
        
        # Check required fields
        assert "error" in data
        assert "message" in data
        assert "details" in data
        
        # Check error code format
        assert isinstance(data["error"], str)
        assert data["error"] == "VLAN_NOT_FOUND"
        
        # Check details structure
        assert isinstance(data["details"], dict)
        assert "vlan_id" in data["details"]
    
    def test_error_response_structure_409(self, client):
        """Test that 409 errors have correct response structure"""
        vlan_data = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        # Create first VLAN
        client.post("/api/v1/vlans", json=vlan_data)
        
        # Try to create duplicate
        response = client.post("/api/v1/vlans", json=vlan_data)
        
        assert response.status_code == 409
        data = response.json()
        
        # Check required fields
        assert "error" in data
        assert "message" in data
        assert "details" in data
        
        # Check error code format
        assert data["error"] == "VLAN_CONFLICT"
        
        # Check details structure
        assert isinstance(data["details"], dict)
        assert "vlan_id" in data["details"]
    
    def test_error_response_structure_422(self, client):
        """Test that 422 errors have correct response structure"""
        invalid_vlan = {
            "name": "Test VLAN",
            "vlan_id": 5000,  # Invalid
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        response = client.post("/api/v1/vlans", json=invalid_vlan)
        
        assert response.status_code == 422
        data = response.json()
        
        # Check required fields
        assert "error" in data
        assert "message" in data
        assert "details" in data
        
        # Check details structure for validation errors
        assert isinstance(data["details"], dict)
        assert "errors" in data["details"]
        assert isinstance(data["details"]["errors"], list)


class TestHealthEndpointErrors:
    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["storage_healthy"] is True
    
    def test_health_check_storage_unhealthy(self, client):
        """Test health check when storage is unhealthy"""
        from unittest.mock import patch
        from app.services.dependency_injection import container
        
        # Get the current repository instance
        repository = container.get_vlan_repository()
        
        # Mock the health_check method to return False (unhealthy)
        with patch.object(repository, 'health_check', return_value=False):
            response = client.get("/health")
            
            assert response.status_code == 503
            data = response.json()
            # The HTTPException detail is returned directly as the response content
            assert data["error"] == "SERVICE_UNHEALTHY"
            assert data["message"] == "Storage system is not accessible"
            assert data["details"]["storage_healthy"] is False