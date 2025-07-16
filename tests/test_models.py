import pytest
from pydantic import ValidationError
from app.api.dto import VLANCreateDTO, VLANUpdateDTO, VLANResponseDTO


class TestVLANModels:
    def test_valid_vlan_create(self):
        """Test creating a valid VLAN"""
        vlan_data = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        vlan = VLANCreateDTO(**vlan_data)
        assert vlan.name == "Test VLAN"
        assert vlan.vlan_id == 100
        assert vlan.subnet == "192.168.1.0/24"
        assert vlan.gateway == "192.168.1.1"
        assert vlan.status == "active"
    
    def test_invalid_vlan_id_too_low(self):
        """Test VLAN ID too low"""
        vlan_data = {
            "name": "Test VLAN",
            "vlan_id": 0,  # Too low
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        with pytest.raises(ValidationError):
            VLANCreateDTO(**vlan_data)
    
    def test_invalid_vlan_id_too_high(self):
        """Test VLAN ID too high"""
        vlan_data = {
            "name": "Test VLAN",
            "vlan_id": 5000,  # Too high
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        with pytest.raises(ValidationError):
            VLANCreateDTO(**vlan_data)
    
    def test_invalid_subnet_format(self):
        """Test invalid subnet format"""
        vlan_data = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "invalid-subnet",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        with pytest.raises(ValidationError):
            VLANCreateDTO(**vlan_data)
    
    def test_invalid_gateway_format(self):
        """Test invalid gateway format"""
        vlan_data = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "invalid-gateway",
            "status": "active"
        }
        
        with pytest.raises(ValidationError):
            VLANCreateDTO(**vlan_data)
    
    def test_gateway_not_in_subnet(self):
        """Test gateway not in subnet"""
        vlan_data = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "10.0.0.1",  # Not in subnet
            "status": "active"
        }
        
        with pytest.raises(ValidationError):
            VLANCreateDTO(**vlan_data)
    
    def test_invalid_status(self):
        """Test invalid status value"""
        vlan_data = {
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "invalid-status"
        }
        
        with pytest.raises(ValidationError):
            VLANCreateDTO(**vlan_data)
    
    def test_valid_statuses(self):
        """Test all valid status values"""
        valid_statuses = ["active", "inactive", "maintenance"]
        
        for status in valid_statuses:
            vlan_data = {
                "name": "Test VLAN",
                "vlan_id": 100,
                "subnet": "192.168.1.0/24",
                "gateway": "192.168.1.1",
                "status": status
            }
            
            vlan = VLANCreateDTO(**vlan_data)
            assert vlan.status == status
    
    def test_name_too_long(self):
        """Test name too long"""
        vlan_data = {
            "name": "x" * 101,  # Too long
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        with pytest.raises(ValidationError):
            VLANCreateDTO(**vlan_data)
    
    def test_vlan_update_partial(self):
        """Test partial VLAN update"""
        update_data = {
            "name": "Updated VLAN",
            "status": "inactive"
        }
        
        vlan_update = VLANUpdateDTO(**update_data)
        assert vlan_update.name == "Updated VLAN"
        assert vlan_update.status == "inactive"
        assert vlan_update.vlan_id is None
        assert vlan_update.subnet is None
        assert vlan_update.gateway is None
    
    def test_vlan_update_empty(self):
        """Test empty VLAN update"""
        vlan_update = VLANUpdateDTO()
        assert vlan_update.name is None
        assert vlan_update.vlan_id is None
        assert vlan_update.subnet is None
        assert vlan_update.gateway is None
        assert vlan_update.status is None
    
    def test_vlan_model_with_id(self):
        """Test VLAN model with ID"""
        vlan_data = {
            "id": 1,
            "name": "Test VLAN",
            "vlan_id": 100,
            "subnet": "192.168.1.0/24",
            "gateway": "192.168.1.1",
            "status": "active"
        }
        
        vlan = VLANResponseDTO(**vlan_data)
        assert vlan.id == 1
        assert vlan.name == "Test VLAN"
    
    def test_different_subnet_formats(self):
        """Test different valid subnet formats"""
        valid_subnets = [
            "192.168.1.0/24",
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16"
        ]
        
        for subnet in valid_subnets:
            vlan_data = {
                "name": "Test VLAN",
                "vlan_id": 100,
                "subnet": subnet,
                "gateway": subnet.split('/')[0].rsplit('.', 1)[0] + ".1",
                "status": "active"
            }
            
            vlan = VLANCreateDTO(**vlan_data)
            assert vlan.subnet == subnet