"""
Data mappers - Convert between DTOs and domain entities
"""
from typing import Dict, Any
from app.domain.entities import VLANEntity
from app.api.dto import VLANResponseDTO


class VLANMapper:
    """Mapper for VLAN entities and DTOs"""
    
    @staticmethod
    def entity_to_response_dto(entity: VLANEntity) -> VLANResponseDTO:
        """Convert domain entity to response DTO"""
        return VLANResponseDTO(
            id=entity.id,
            name=entity.name,
            vlan_id=entity.vlan_id,
            subnet=entity.subnet,
            gateway=entity.gateway,
            status=entity.status
        )
    
    @staticmethod
    def create_dto_to_dict(dto) -> Dict[str, Any]:
        """Convert create DTO to dictionary"""
        return dto.model_dump()
    
    @staticmethod
    def update_dto_to_dict(dto) -> Dict[str, Any]:
        """Convert update DTO to dictionary (exclude unset fields)"""
        return dto.model_dump(exclude_unset=True)
    
