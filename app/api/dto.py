"""
Data Transfer Objects (DTOs) - API layer data contracts
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Literal, List
from datetime import datetime
import ipaddress


class VLANResponseDTO(BaseModel):
    """DTO for VLAN response"""
    id: int = Field(..., description="Unique identifier for the VLAN")
    name: str = Field(..., description="Human-readable name for the VLAN")
    vlan_id: int = Field(..., description="VLAN ID")
    subnet: str = Field(..., description="Subnet in CIDR notation")
    gateway: str = Field(..., description="Gateway IP address")
    status: Literal["active", "inactive", "maintenance"] = Field(..., description="Current status")
    
    model_config = ConfigDict(from_attributes=True)


class VLANCreateDTO(BaseModel):
    """DTO for creating VLANs"""
    name: str = Field(..., min_length=1, max_length=100, description="Human-readable name")
    vlan_id: int = Field(..., ge=1, le=4094, description="VLAN ID")
    subnet: str = Field(..., description="Subnet in CIDR notation")
    gateway: str = Field(..., description="Gateway IP address")
    status: Literal["active", "inactive", "maintenance"] = Field(
        default="active",
        description="Current status"
    )
    
    @field_validator('subnet')
    @classmethod
    def validate_subnet(cls, v):
        try:
            ipaddress.ip_network(v, strict=False)
        except ValueError:
            raise ValueError('Invalid subnet format. Use CIDR notation (e.g., 192.168.1.0/24)')
        return v
    
    @field_validator('gateway')
    @classmethod
    def validate_gateway(cls, v, info):
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError('Invalid gateway IP address format')
        
        # Validate gateway is in subnet if subnet is provided
        if info.data and 'subnet' in info.data:
            try:
                network = ipaddress.ip_network(info.data['subnet'], strict=False)
                gateway = ipaddress.ip_address(v)
                if gateway not in network:
                    raise ValueError(f'Gateway {gateway} is not in subnet {network}')
            except ValueError as e:
                if 'Gateway' in str(e):
                    raise
        return v


class VLANUpdateDTO(BaseModel):
    """DTO for updating VLANs"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    vlan_id: Optional[int] = Field(None, ge=1, le=4094)
    subnet: Optional[str] = Field(None)
    gateway: Optional[str] = Field(None)
    status: Optional[Literal["active", "inactive", "maintenance"]] = Field(None)
    
    @field_validator('subnet')
    @classmethod
    def validate_subnet(cls, v):
        if v is not None:
            try:
                ipaddress.ip_network(v, strict=False)
            except ValueError:
                raise ValueError('Invalid subnet format. Use CIDR notation (e.g., 192.168.1.0/24)')
        return v
    
    @field_validator('gateway')
    @classmethod
    def validate_gateway(cls, v):
        if v is not None:
            try:
                ipaddress.ip_address(v)
            except ValueError:
                raise ValueError('Invalid gateway IP address format')
        return v


class HealthResponseDTO(BaseModel):
    """DTO for health check response"""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Timestamp of health check")
    version: str = Field(..., description="API version")
    storage_healthy: bool = Field(..., description="Storage system health")



