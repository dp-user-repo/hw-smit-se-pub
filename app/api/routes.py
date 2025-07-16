"""
API routes - Endpoint implementations
"""

from fastapi import APIRouter, status, Depends
from typing import List
from datetime import datetime

from app.api.dto import VLANResponseDTO, VLANCreateDTO, VLANUpdateDTO, HealthResponseDTO
from app.api.mappers import VLANMapper
from app.services.vlan_service import VLANService
from app.services.dependency_injection import container


router = APIRouter()


def get_vlan_service() -> VLANService:
    """Dependency injection for VLAN service"""
    return container.get_vlan_service()


@router.get("/api/v1/vlans", response_model=List[VLANResponseDTO], tags=["VLANs"])
async def get_all_vlans(service: VLANService = Depends(get_vlan_service)):
    """Get all VLANs"""
    vlans = service.get_all_vlans()
    return [VLANMapper.entity_to_response_dto(vlan) for vlan in vlans]


@router.post("/api/v1/vlans", response_model=VLANResponseDTO, status_code=status.HTTP_201_CREATED, tags=["VLANs"])
async def create_vlan(
    vlan: VLANCreateDTO,
    service: VLANService = Depends(get_vlan_service)
):
    """Create a new VLAN"""
    vlan_data = VLANMapper.create_dto_to_dict(vlan)
    created_vlan = service.create_vlan(vlan_data)
    return VLANMapper.entity_to_response_dto(created_vlan)


@router.get("/api/v1/vlans/{vlan_id}", response_model=VLANResponseDTO, tags=["VLANs"])
async def get_vlan(
    vlan_id: int,
    service: VLANService = Depends(get_vlan_service)
):
    """Get a specific VLAN by ID"""
    vlan = service.get_vlan_by_id(vlan_id)
    return VLANMapper.entity_to_response_dto(vlan)


@router.put("/api/v1/vlans/{vlan_id}", response_model=VLANResponseDTO, tags=["VLANs"])
async def update_vlan(
    vlan_id: int,
    vlan_update: VLANUpdateDTO,
    service: VLANService = Depends(get_vlan_service)
):
    """Update a VLAN"""
    update_data = VLANMapper.update_dto_to_dict(vlan_update)
    updated_vlan = service.update_vlan(vlan_id, update_data)
    return VLANMapper.entity_to_response_dto(updated_vlan)


@router.delete("/api/v1/vlans/{vlan_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["VLANs"])
async def delete_vlan(
    vlan_id: int,
    service: VLANService = Depends(get_vlan_service)
):
    """Delete a VLAN"""
    service.delete_vlan(vlan_id)
    return None


@router.get("/health", response_model=HealthResponseDTO, tags=["Health"])
async def health_check(service: VLANService = Depends(get_vlan_service)):
    """Health check endpoint"""
    is_healthy = service.health_check()
    
    if not is_healthy:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "SERVICE_UNHEALTHY", 
                "message": "Storage system is not accessible",
                "details": {"storage_healthy": False}
            }
        )
    
    return HealthResponseDTO(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        storage_healthy=is_healthy
    )


