import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from app.main import create_app, app
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


@pytest.fixture
def sample_vlan():
    """Sample VLAN data for testing"""
    return {
        "name": "Test VLAN",
        "vlan_id": 100,
        "subnet": "192.168.1.0/24",
        "gateway": "192.168.1.1",
        "status": "active"
    }


class TestVLANAPI:
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
        assert data["storage_healthy"] == True
    
    def test_get_all_vlans_empty(self, client):
        """Test getting all VLANs when empty"""
        response = client.get("/api/v1/vlans")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_vlan(self, client, sample_vlan):
        """Test creating a new VLAN"""
        response = client.post("/api/v1/vlans", json=sample_vlan)
        assert response.status_code == 201
        
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test VLAN"
        assert data["vlan_id"] == 100
        assert data["subnet"] == "192.168.1.0/24"
        assert data["gateway"] == "192.168.1.1"
        assert data["status"] == "active"
    
    def test_create_vlan_invalid_data(self, client):
        """Test creating VLAN with invalid data"""
        invalid_vlan = {
            "name": "Test VLAN",
            "vlan_id": 5000,  # Out of range
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        response = client.post("/api/v1/vlans", json=invalid_vlan)
        assert response.status_code == 422
    
    def test_create_vlan_invalid_ip(self, client):
        """Test creating VLAN with invalid IP formats"""
        invalid_vlan = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "invalid-subnet",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        response = client.post("/api/v1/vlans", json=invalid_vlan)
        assert response.status_code == 422
    
    def test_create_vlan_gateway_not_in_subnet(self, client):
        """Test creating VLAN with gateway not in subnet"""
        invalid_vlan = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "10.0.0.1",  # Not in subnet
            "status": "active"
        }
        
        response = client.post("/api/v1/vlans", json=invalid_vlan)
        assert response.status_code == 422
    
    def test_create_duplicate_vlan_id(self, client, sample_vlan):
        """Test creating VLAN with duplicate VLAN ID"""
        # Create first VLAN
        response = client.post("/api/v1/vlans", json=sample_vlan)
        assert response.status_code == 201
        
        # Try to create another with same VLAN ID
        response = client.post("/api/v1/vlans", json=sample_vlan)
        assert response.status_code == 409
        
        data = response.json()
        assert data["error"] == "VLAN_CONFLICT"
    
    def test_get_all_vlans_with_data(self, client, sample_vlan):
        """Test getting all VLANs with data"""
        # Create a VLAN first
        client.post("/api/v1/vlans", json=sample_vlan)
        
        response = client.get("/api/v1/vlans")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test VLAN"
    
    def test_get_vlan_by_id(self, client, sample_vlan):
        """Test getting VLAN by ID"""
        # Create a VLAN first
        create_response = client.post("/api/v1/vlans", json=sample_vlan)
        created_vlan = create_response.json()
        
        response = client.get(f"/api/v1/vlans/{created_vlan['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == created_vlan["id"]
        assert data["name"] == "Test VLAN"
    
    def test_get_vlan_by_id_not_found(self, client):
        """Test getting non-existent VLAN by ID"""
        response = client.get("/api/v1/vlans/999")
        assert response.status_code == 404
        
        data = response.json()
        assert data["error"] == "VLAN_NOT_FOUND"
    
    def test_update_vlan(self, client, sample_vlan):
        """Test updating a VLAN"""
        # Create a VLAN first
        create_response = client.post("/api/v1/vlans", json=sample_vlan)
        created_vlan = create_response.json()
        
        update_data = {
            "name": "Updated VLAN",
            "status": "inactive"
        }
        
        response = client.put(f"/api/v1/vlans/{created_vlan['id']}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated VLAN"
        assert data["status"] == "inactive"
        assert data["vlan_id"] == 100  # Unchanged
    
    def test_update_vlan_not_found(self, client):
        """Test updating non-existent VLAN"""
        update_data = {"name": "Updated VLAN"}
        
        response = client.put("/api/v1/vlans/999", json=update_data)
        assert response.status_code == 404
        
        data = response.json()
        assert data["error"] == "VLAN_NOT_FOUND"
    
    def test_update_vlan_conflict(self, client, sample_vlan):
        """Test updating VLAN with conflicting VLAN ID"""
        # Create two VLANs
        client.post("/api/v1/vlans", json=sample_vlan)
        
        second_vlan = {
            "name": "Second VLAN",
            "vlan_id": 200,
            "subnet": "192.168.2.0/24",
            "gateway": "192.168.2.1",
            "status": "active"
        }
        create_response = client.post("/api/v1/vlans", json=second_vlan)
        created_vlan = create_response.json()
        
        # Try to update second VLAN with first VLAN's VLAN ID
        update_data = {"vlan_id": 100}
        
        response = client.put(f"/api/v1/vlans/{created_vlan['id']}", json=update_data)
        assert response.status_code == 409
        
        data = response.json()
        assert data["error"] == "VLAN_CONFLICT"
    
    def test_delete_vlan(self, client, sample_vlan):
        """Test deleting a VLAN"""
        # Create a VLAN first
        create_response = client.post("/api/v1/vlans", json=sample_vlan)
        created_vlan = create_response.json()
        
        response = client.delete(f"/api/v1/vlans/{created_vlan['id']}")
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(f"/api/v1/vlans/{created_vlan['id']}")
        assert response.status_code == 404
    
    def test_delete_vlan_not_found(self, client):
        """Test deleting non-existent VLAN"""
        response = client.delete("/api/v1/vlans/999")
        assert response.status_code == 404
        
        data = response.json()
        assert data["error"] == "VLAN_NOT_FOUND"
    
    def test_api_workflow(self, client, sample_vlan):
        """Test complete API workflow"""
        # 1. Start with empty list
        response = client.get("/api/v1/vlans")
        assert response.status_code == 200
        assert len(response.json()) == 0
        
        # 2. Create a VLAN
        create_response = client.post("/api/v1/vlans", json=sample_vlan)
        assert create_response.status_code == 201
        created_vlan = create_response.json()
        
        # 3. Get all VLANs
        response = client.get("/api/v1/vlans")
        assert response.status_code == 200
        assert len(response.json()) == 1
        
        # 4. Get specific VLAN
        response = client.get(f"/api/v1/vlans/{created_vlan['id']}")
        assert response.status_code == 200
        
        # 5. Update VLAN
        update_data = {"name": "Updated VLAN"}
        response = client.put(f"/api/v1/vlans/{created_vlan['id']}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated VLAN"
        
        # 6. Delete VLAN
        response = client.delete(f"/api/v1/vlans/{created_vlan['id']}")
        assert response.status_code == 204
        
        # 7. Verify empty list
        response = client.get("/api/v1/vlans")
        assert response.status_code == 200
        assert len(response.json()) == 0


class TestAppConfiguration:
    def test_app_configuration(self):
        """Test that the app can be created"""
        assert app is not None
        assert app.title == "VLAN Management API"
    
    def test_route_registration(self):
        """Test that the endpoints are defined"""
        # Check that our endpoints are in the routes
        route_paths = [route.path for route in app.routes]
        
        expected_paths = [
            "/api/v1/vlans",
            "/api/v1/vlans/{vlan_id}",
            "/health"
        ]
        
        for path in expected_paths:
            assert any(path == route_path or path in route_path for route_path in route_paths)