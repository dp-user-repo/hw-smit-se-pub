"""
Factory implementations - Object creation patterns
"""
import os
from app.domain.repositories import VLANRepository
from app.infrastructure.repositories import JSONVLANRepository


class RepositoryFactory:
    """Factory for creating repository instances"""
    
    @staticmethod
    def create_vlan_repository(storage_type: str = "json", **kwargs) -> VLANRepository:
        """Create VLAN repository based on storage type"""
        if storage_type == "json":
            # Use environment variable first, then kwargs, then default
            file_path = os.getenv("DATA_FILE_PATH") or kwargs.get("file_path", "vlans.json")
            
            # Fallback: Use container path if running in Docker and no env var is set
            if not os.getenv("DATA_FILE_PATH") and os.path.exists("/app/data"):
                file_path = os.path.join("/app/data", os.path.basename(file_path))
            
            return JSONVLANRepository(file_path)
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")


class VLANEntityFactory:
    """Factory for creating VLAN entities"""
    
    @staticmethod
    def create_from_dict(data: dict, next_id: int = None) -> "VLANEntity":
        """Create VLAN entity from dictionary"""
        from app.domain.entities import VLANEntity
        
        # Use provided ID or generate new one
        vlan_id = data.get("id", next_id)
        if vlan_id is None:
            raise ValueError("VLAN ID is required")
        
        return VLANEntity(
            id=vlan_id,
            name=data["name"],
            vlan_id=data["vlan_id"],
            subnet=data["subnet"],
            gateway=data["gateway"],
            status=data["status"]
        )