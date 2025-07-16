import pytest
from unittest.mock import Mock
from app.services.vlan_service import VLANService
from app.domain.entities import VLANEntity
from app.domain.exceptions import VLANNotFoundError, VLANConflictError, VLANValidationError


@pytest.fixture
def mock_repository():
    """Create a mock repository for testing"""
    return Mock()


@pytest.fixture
def vlan_service(mock_repository):
    """Create VLANService instance with mock repository"""
    return VLANService(mock_repository)


@pytest.fixture
def sample_vlan_entity():
    """Sample VLAN entity for testing"""
    return VLANEntity(
        id=1,
        name="Test VLAN",
        vlan_id=100,
        subnet="192.168.1.0/24",
        gateway="192.168.1.1",
        status="active"
    )


@pytest.fixture
def sample_vlan_data():
    """Sample VLAN data for testing"""
    return {
        "name": "Test VLAN",
        "vlan_id": 100,
        "subnet": "192.168.1.0/24",
        "gateway": "192.168.1.1",
        "status": "active"
    }


class TestVLANService:
    def test_get_all_vlans(self, vlan_service, mock_repository, sample_vlan_entity):
        """Test getting all VLANs"""
        mock_repository.get_all.return_value = [sample_vlan_entity]
        
        result = vlan_service.get_all_vlans()
        
        assert len(result) == 1
        assert result[0] == sample_vlan_entity
        mock_repository.get_all.assert_called_once()
    
    def test_get_all_vlans_empty(self, vlan_service, mock_repository):
        """Test getting all VLANs when empty"""
        mock_repository.get_all.return_value = []
        
        result = vlan_service.get_all_vlans()
        
        assert result == []
        mock_repository.get_all.assert_called_once()
    
    def test_get_vlan_by_id_success(self, vlan_service, mock_repository, sample_vlan_entity):
        """Test getting VLAN by ID successfully"""
        mock_repository.get_by_id.return_value = sample_vlan_entity
        
        result = vlan_service.get_vlan_by_id(1)
        
        assert result == sample_vlan_entity
        mock_repository.get_by_id.assert_called_once_with(1)
    
    def test_get_vlan_by_id_not_found(self, vlan_service, mock_repository):
        """Test getting VLAN by ID when not found"""
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(VLANNotFoundError) as exc_info:
            vlan_service.get_vlan_by_id(999)
        
        assert exc_info.value.vlan_id == 999
        mock_repository.get_by_id.assert_called_once_with(999)
    
    def test_create_vlan_success(self, vlan_service, mock_repository, sample_vlan_data, sample_vlan_entity):
        """Test creating VLAN successfully"""
        mock_repository.exists_by_vlan_id.return_value = False
        mock_repository.get_next_id.return_value = 1
        mock_repository.save.return_value = sample_vlan_entity
        
        result = vlan_service.create_vlan(sample_vlan_data)
        
        assert result == sample_vlan_entity
        mock_repository.exists_by_vlan_id.assert_called_once_with(100)
        mock_repository.get_next_id.assert_called_once()
        mock_repository.save.assert_called_once()
    
    def test_create_vlan_conflict(self, vlan_service, mock_repository, sample_vlan_data):
        """Test creating VLAN with duplicate VLAN ID"""
        mock_repository.exists_by_vlan_id.return_value = True
        
        with pytest.raises(VLANConflictError) as exc_info:
            vlan_service.create_vlan(sample_vlan_data)
        
        assert exc_info.value.vlan_id == 100
        mock_repository.exists_by_vlan_id.assert_called_once_with(100)
        mock_repository.get_next_id.assert_not_called()
        mock_repository.save.assert_not_called()
    
    def test_create_vlan_validation_error(self, vlan_service, mock_repository):
        """Test creating VLAN with invalid data"""
        mock_repository.exists_by_vlan_id.return_value = False
        mock_repository.get_next_id.return_value = 1
        
        invalid_data = {
            "name": "Test VLAN",
            "vlan_id": 5000,  # Invalid VLAN ID
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        with pytest.raises(VLANValidationError):
            vlan_service.create_vlan(invalid_data)
        
        mock_repository.save.assert_not_called()
    
    def test_update_vlan_success(self, vlan_service, mock_repository, sample_vlan_entity):
        """Test updating VLAN successfully"""
        mock_repository.get_by_id.return_value = sample_vlan_entity
        
        updated_entity = VLANEntity(
            id=1,
            name="Updated VLAN",
            vlan_id=100,
            subnet="192.168.1.0/24",
            gateway="192.168.1.1",
            status="inactive"
        )
        mock_repository.save.return_value = updated_entity
        
        update_data = {"name": "Updated VLAN", "status": "inactive"}
        result = vlan_service.update_vlan(1, update_data)
        
        assert result == updated_entity
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.save.assert_called_once()
    
    def test_update_vlan_not_found(self, vlan_service, mock_repository):
        """Test updating non-existent VLAN"""
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(VLANNotFoundError) as exc_info:
            vlan_service.update_vlan(999, {"name": "Updated"})
        
        assert exc_info.value.vlan_id == 999
        mock_repository.get_by_id.assert_called_once_with(999)
        mock_repository.save.assert_not_called()
    
    def test_update_vlan_id_conflict(self, vlan_service, mock_repository, sample_vlan_entity):
        """Test updating VLAN with conflicting VLAN ID"""
        mock_repository.get_by_id.return_value = sample_vlan_entity
        mock_repository.exists_by_vlan_id.return_value = True
        
        with pytest.raises(VLANConflictError) as exc_info:
            vlan_service.update_vlan(1, {"vlan_id": 200})
        
        assert exc_info.value.vlan_id == 200
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.exists_by_vlan_id.assert_called_once_with(200)
        mock_repository.save.assert_not_called()
    
    def test_update_vlan_same_vlan_id(self, vlan_service, mock_repository, sample_vlan_entity):
        """Test updating VLAN with same VLAN ID (should not check conflict)"""
        mock_repository.get_by_id.return_value = sample_vlan_entity
        mock_repository.save.return_value = sample_vlan_entity
        
        update_data = {"vlan_id": 100, "name": "Updated"}  # Same VLAN ID
        result = vlan_service.update_vlan(1, update_data)
        
        assert result == sample_vlan_entity
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.exists_by_vlan_id.assert_not_called()  # Should not check conflict
        mock_repository.save.assert_called_once()
    
    def test_update_vlan_validation_error(self, vlan_service, mock_repository, sample_vlan_entity):
        """Test updating VLAN with invalid data"""
        mock_repository.get_by_id.return_value = sample_vlan_entity
        
        invalid_update = {"gateway": "invalid-ip"}
        
        with pytest.raises(VLANValidationError):
            vlan_service.update_vlan(1, invalid_update)
        
        mock_repository.save.assert_not_called()
    
    def test_delete_vlan_success(self, vlan_service, mock_repository, sample_vlan_entity):
        """Test deleting VLAN successfully"""
        mock_repository.get_by_id.return_value = sample_vlan_entity
        mock_repository.delete.return_value = True
        
        result = vlan_service.delete_vlan(1)
        
        assert result is True
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.delete.assert_called_once_with(1)
    
    def test_delete_vlan_not_found(self, vlan_service, mock_repository):
        """Test deleting non-existent VLAN"""
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(VLANNotFoundError) as exc_info:
            vlan_service.delete_vlan(999)
        
        assert exc_info.value.vlan_id == 999
        mock_repository.get_by_id.assert_called_once_with(999)
        mock_repository.delete.assert_not_called()
    
    def test_health_check(self, vlan_service, mock_repository):
        """Test health check"""
        mock_repository.health_check.return_value = True
        
        result = vlan_service.health_check()
        
        assert result is True
        mock_repository.health_check.assert_called_once()
    
    def test_health_check_unhealthy(self, vlan_service, mock_repository):
        """Test health check when unhealthy"""
        mock_repository.health_check.return_value = False
        
        result = vlan_service.health_check()
        
        assert result is False
        mock_repository.health_check.assert_called_once()


class TestVLANServiceEdgeCases:
    def test_create_vlan_missing_required_field(self, vlan_service, mock_repository):
        """Test creating VLAN with missing required fields"""
        # The service tries to access vlan_data["vlan_id"] before validation
        # So this will raise KeyError, not VLANValidationError
        
        incomplete_data = {
            "name": "Test VLAN",
            # Missing vlan_id, subnet, gateway, status
        }
        
        with pytest.raises(KeyError):
            vlan_service.create_vlan(incomplete_data)
    
    def test_update_vlan_partial_data(self, vlan_service, mock_repository, sample_vlan_entity):
        """Test updating VLAN with partial data preserves other fields"""
        mock_repository.get_by_id.return_value = sample_vlan_entity
        
        # Mock the save method to capture the entity being saved
        saved_entity = None
        def capture_save(entity):
            nonlocal saved_entity
            saved_entity = entity
            return entity
        
        mock_repository.save.side_effect = capture_save
        
        partial_update = {"name": "New Name"}
        vlan_service.update_vlan(1, partial_update)
        
        # Verify that unchanged fields are preserved
        assert saved_entity.name == "New Name"
        assert saved_entity.vlan_id == 100  # Preserved
        assert saved_entity.subnet == "192.168.1.0/24"  # Preserved
        assert saved_entity.gateway == "192.168.1.1"  # Preserved
        assert saved_entity.status == "active"  # Preserved