"""
Repository implementations - Concrete data access layer
"""
import json
import os
from typing import List, Optional, Dict, Any
from app.domain.entities import VLANEntity
from app.domain.repositories import VLANRepository
from app.domain.exceptions import StorageError


class JSONVLANRepository(VLANRepository):
    """JSON file-based VLAN repository implementation"""
    
    def __init__(self, file_path: str = "vlans.json"):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the JSON file exists with proper structure"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({"vlans": [], "next_id": 1}, f, indent=2)
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                if "vlans" not in data or "next_id" not in data:
                    return {"vlans": [], "next_id": 1}
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return {"vlans": [], "next_id": 1}
    
    def _save_data(self, data: Dict[str, Any]) -> None:
        """Save data to JSON file"""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise StorageError(f"Failed to save data: {e}")
    
    def _vlan_dict_to_entity(self, vlan_dict: Dict[str, Any]) -> VLANEntity:
        """Convert dictionary to VLAN entity"""
        return VLANEntity(
            id=vlan_dict["id"],
            name=vlan_dict["name"],
            vlan_id=vlan_dict["vlan_id"],
            subnet=vlan_dict["subnet"],
            gateway=vlan_dict["gateway"],
            status=vlan_dict["status"]
        )
    
    def _entity_to_dict(self, vlan: VLANEntity) -> Dict[str, Any]:
        """Convert VLAN entity to dictionary"""
        return {
            "id": vlan.id,
            "name": vlan.name,
            "vlan_id": vlan.vlan_id,
            "subnet": vlan.subnet,
            "gateway": vlan.gateway,
            "status": vlan.status
        }
    
    def get_all(self) -> List[VLANEntity]:
        """Get all VLANs"""
        data = self._load_data()
        return [self._vlan_dict_to_entity(vlan_dict) for vlan_dict in data["vlans"]]
    
    def get_by_id(self, vlan_id: int) -> Optional[VLANEntity]:
        """Get VLAN by internal ID"""
        data = self._load_data()
        for vlan_dict in data["vlans"]:
            if vlan_dict["id"] == vlan_id:
                return self._vlan_dict_to_entity(vlan_dict)
        return None
    
    def get_by_vlan_id(self, vlan_id: int) -> Optional[VLANEntity]:
        """Get VLAN by VLAN ID"""
        data = self._load_data()
        for vlan_dict in data["vlans"]:
            if vlan_dict["vlan_id"] == vlan_id:
                return self._vlan_dict_to_entity(vlan_dict)
        return None
    
    def save(self, vlan: VLANEntity) -> VLANEntity:
        """Save VLAN (create or update)"""
        data = self._load_data()
        
        # Check if updating existing VLAN
        for i, vlan_dict in enumerate(data["vlans"]):
            if vlan_dict["id"] == vlan.id:
                # Update existing
                data["vlans"][i] = self._entity_to_dict(vlan)
                self._save_data(data)
                return vlan
        
        # Create new VLAN
        data["vlans"].append(self._entity_to_dict(vlan))
        if vlan.id >= data["next_id"]:
            data["next_id"] = vlan.id + 1
        
        self._save_data(data)
        return vlan
    
    def delete(self, vlan_id: int) -> bool:
        """Delete VLAN by internal ID"""
        data = self._load_data()
        
        for i, vlan_dict in enumerate(data["vlans"]):
            if vlan_dict["id"] == vlan_id:
                del data["vlans"][i]
                self._save_data(data)
                return True
        
        return False
    
    def exists_by_vlan_id(self, vlan_id: int, exclude_id: Optional[int] = None) -> bool:
        """Check if VLAN ID exists, optionally excluding specific internal ID"""
        data = self._load_data()
        for vlan_dict in data["vlans"]:
            if vlan_dict["vlan_id"] == vlan_id:
                if exclude_id is None or vlan_dict["id"] != exclude_id:
                    return True
        return False
    
    def get_next_id(self) -> int:
        """Get next available internal ID"""
        data = self._load_data()
        return data["next_id"]
    
    def health_check(self) -> bool:
        """Check repository health"""
        try:
            self._load_data()
            return True
        except StorageError:
            return False