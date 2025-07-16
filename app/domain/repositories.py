"""
Repository interfaces - Abstract data access layer
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import VLANEntity


class VLANRepository(ABC):
    """Abstract repository for VLAN data access"""
    
    @abstractmethod
    def get_all(self) -> List[VLANEntity]:
        """Get all VLANs"""
        pass
    
    @abstractmethod
    def get_by_id(self, vlan_id: int) -> Optional[VLANEntity]:
        """Get VLAN by internal ID"""
        pass
    
    @abstractmethod
    def get_by_vlan_id(self, vlan_id: int) -> Optional[VLANEntity]:
        """Get VLAN by VLAN ID"""
        pass
    
    @abstractmethod
    def save(self, vlan: VLANEntity) -> VLANEntity:
        """Save VLAN (create or update)"""
        pass
    
    @abstractmethod
    def delete(self, vlan_id: int) -> bool:
        """Delete VLAN by internal ID"""
        pass
    
    @abstractmethod
    def exists_by_vlan_id(self, vlan_id: int, exclude_id: Optional[int] = None) -> bool:
        """Check if VLAN ID exists, optionally excluding specific internal ID"""
        pass
    
    @abstractmethod
    def get_next_id(self) -> int:
        """Get next available internal ID"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check repository health"""
        pass