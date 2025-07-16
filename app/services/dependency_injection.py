"""
Dependency injection container - IoC pattern
"""
from typing import Optional
from app.domain.repositories import VLANRepository
from app.services.vlan_service import VLANService
from app.infrastructure.factories import RepositoryFactory


class DIContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._vlan_repository: Optional[VLANRepository] = None
        self._vlan_service: Optional[VLANService] = None
    
    def get_vlan_repository(self, storage_type: str = "json", **kwargs) -> VLANRepository:
        """Get VLAN repository instance (singleton)"""
        if self._vlan_repository is None:
            self._vlan_repository = RepositoryFactory.create_vlan_repository(
                storage_type=storage_type, **kwargs
            )
        return self._vlan_repository
    
    def get_vlan_service(self, storage_type: str = "json", **kwargs) -> VLANService:
        """Get VLAN service instance (singleton)"""
        if self._vlan_service is None:
            repository = self.get_vlan_repository(storage_type=storage_type, **kwargs)
            self._vlan_service = VLANService(repository)
        return self._vlan_service
    
    def reset(self):
        """Reset container (useful for testing)"""
        self._vlan_repository = None
        self._vlan_service = None


# Global container instance
container = DIContainer()