"""
Service layer - Business logic implementation
"""
from typing import List, Optional, Dict, Any
from app.domain.entities import VLANEntity
from app.domain.repositories import VLANRepository
from app.domain.exceptions import VLANNotFoundError, VLANConflictError, VLANValidationError
from app.infrastructure.factories import VLANEntityFactory


class VLANService:
    """Service for VLAN business logic"""
    
    def __init__(self, repository: VLANRepository):
        self._repository = repository
    
    def get_all_vlans(self) -> List[VLANEntity]:
        """Get all VLANs"""
        return self._repository.get_all()
    
    def get_vlan_by_id(self, vlan_id: int) -> VLANEntity:
        """Get VLAN by internal ID"""
        vlan = self._repository.get_by_id(vlan_id)
        if not vlan:
            raise VLANNotFoundError(vlan_id)
        return vlan
    
    def create_vlan(self, vlan_data: Dict[str, Any]) -> VLANEntity:
        """Create new VLAN"""
        # Check for VLAN ID conflicts
        if self._repository.exists_by_vlan_id(vlan_data["vlan_id"]):
            raise VLANConflictError(vlan_data["vlan_id"])
        
        # Get next available ID
        next_id = self._repository.get_next_id()
        
        # Create VLAN entity (validates automatically)
        try:
            vlan = VLANEntityFactory.create_from_dict(vlan_data, next_id)
        except (ValueError, KeyError) as e:
            raise VLANValidationError(str(e))
        
        # Save to repository
        return self._repository.save(vlan)
    
    def update_vlan(self, vlan_id: int, update_data: Dict[str, Any]) -> VLANEntity:
        """Update existing VLAN"""
        # Get existing VLAN
        existing_vlan = self._repository.get_by_id(vlan_id)
        if not existing_vlan:
            raise VLANNotFoundError(vlan_id)
        
        # Check for VLAN ID conflicts if updating vlan_id
        if "vlan_id" in update_data and update_data["vlan_id"] != existing_vlan.vlan_id:
            if self._repository.exists_by_vlan_id(update_data["vlan_id"]):
                raise VLANConflictError(update_data["vlan_id"])
        
        # Create updated VLAN data
        updated_data = {
            "id": existing_vlan.id,
            "name": update_data.get("name", existing_vlan.name),
            "vlan_id": update_data.get("vlan_id", existing_vlan.vlan_id),
            "subnet": update_data.get("subnet", existing_vlan.subnet),
            "gateway": update_data.get("gateway", existing_vlan.gateway),
            "status": update_data.get("status", existing_vlan.status)
        }
        
        # Create updated VLAN entity (validates automatically)
        try:
            updated_vlan = VLANEntityFactory.create_from_dict(updated_data)
        except (ValueError, KeyError) as e:
            raise VLANValidationError(str(e))
        
        # Save to repository
        return self._repository.save(updated_vlan)
    
    def delete_vlan(self, vlan_id: int) -> bool:
        """Delete VLAN by internal ID"""
        # Check if VLAN exists
        if not self._repository.get_by_id(vlan_id):
            raise VLANNotFoundError(vlan_id)
        
        return self._repository.delete(vlan_id)
    
    def health_check(self) -> bool:
        """Check service health"""
        return self._repository.health_check()
    
