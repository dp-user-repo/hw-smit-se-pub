import pytest
import os
import tempfile
from app.infrastructure.repositories import JSONVLANRepository
from app.domain.entities import VLANEntity


@pytest.fixture
def temp_repository():
    """Create a temporary repository instance for testing"""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    repository = JSONVLANRepository(temp_file.name)
    yield repository
    os.unlink(temp_file.name)


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


class TestVLANRepository:
    def test_save_vlan(self, temp_repository, sample_vlan_entity):
        """Test saving a new VLAN"""
        vlan = temp_repository.save(sample_vlan_entity)
        
        assert vlan.id == 1
        assert vlan.name == "Test VLAN"
        assert vlan.vlan_id == 100
        assert vlan.subnet == "192.168.1.0/24"
        assert vlan.gateway == "192.168.1.1"
        assert vlan.status == "active"
    
    def test_get_all_vlans(self, temp_repository, sample_vlan_entity):
        """Test getting all VLANs"""
        # Initially empty
        vlans = temp_repository.get_all()
        assert len(vlans) == 0
        
        # Add a VLAN
        temp_repository.save(sample_vlan_entity)
        vlans = temp_repository.get_all()
        assert len(vlans) == 1
        assert vlans[0].name == "Test VLAN"
    
    def test_get_vlan_by_id(self, temp_repository, sample_vlan_entity):
        """Test getting VLAN by ID"""
        temp_repository.save(sample_vlan_entity)
        
        # Get existing VLAN
        vlan = temp_repository.get_by_id(1)
        assert vlan.name == "Test VLAN"
        
        # Get non-existing VLAN
        vlan = temp_repository.get_by_id(999)
        assert vlan is None
    
    def test_get_vlan_by_vlan_id(self, temp_repository, sample_vlan_entity):
        """Test getting VLAN by VLAN ID"""
        temp_repository.save(sample_vlan_entity)
        
        # Get existing VLAN
        vlan = temp_repository.get_by_vlan_id(100)
        assert vlan.name == "Test VLAN"
        
        # Get non-existing VLAN
        vlan = temp_repository.get_by_vlan_id(999)
        assert vlan is None
    
    def test_update_vlan(self, temp_repository, sample_vlan_entity):
        """Test updating a VLAN"""
        temp_repository.save(sample_vlan_entity)
        
        # Create updated entity
        updated_entity = VLANEntity(
            id=1,
            name="Updated VLAN",
            vlan_id=100,
            subnet="192.168.1.0/24",
            gateway="192.168.1.1",
            status="inactive"
        )
        
        updated_vlan = temp_repository.save(updated_entity)
        
        assert updated_vlan.name == "Updated VLAN"
        assert updated_vlan.status == "inactive"
        assert updated_vlan.vlan_id == 100
    
    def test_delete_vlan(self, temp_repository, sample_vlan_entity):
        """Test deleting a VLAN"""
        temp_repository.save(sample_vlan_entity)
        
        # Delete existing VLAN
        success = temp_repository.delete(1)
        assert success is True
        
        # Verify it's deleted
        vlan = temp_repository.get_by_id(1)
        assert vlan is None
    
    def test_delete_nonexistent_vlan(self, temp_repository):
        """Test deleting non-existent VLAN"""
        success = temp_repository.delete(999)
        assert success is False
    
    def test_exists_by_vlan_id(self, temp_repository, sample_vlan_entity):
        """Test checking if VLAN ID exists"""
        # Initially doesn't exist
        assert temp_repository.exists_by_vlan_id(100) is False
        
        # After saving, it exists
        temp_repository.save(sample_vlan_entity)
        assert temp_repository.exists_by_vlan_id(100) is True
        
        # Exclude specific ID
        assert temp_repository.exists_by_vlan_id(100, exclude_id=1) is False
        assert temp_repository.exists_by_vlan_id(100, exclude_id=2) is True
    
    def test_get_next_id(self, temp_repository):
        """Test getting next available ID"""
        # Initially should be 1
        assert temp_repository.get_next_id() == 1
        
        # After saving one VLAN, should be 2
        vlan = VLANEntity(
            id=1,
            name="Test VLAN",
            vlan_id=100,
            subnet="192.168.1.0/24",
            gateway="192.168.1.1",
            status="active"
        )
        temp_repository.save(vlan)
        assert temp_repository.get_next_id() == 2
   
    def test_health_check(self, temp_repository):
        """Test health check"""
        assert temp_repository.health_check() is True
    
    def test_invalid_file_recovery(self):
        """Test recovery from invalid JSON file"""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(b"invalid json content")
        temp_file.close()
        
        repository = JSONVLANRepository(temp_file.name)
        
        # Should recover gracefully
        vlans = repository.get_all()
        assert len(vlans) == 0
        
        os.unlink(temp_file.name)