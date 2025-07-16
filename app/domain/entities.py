"""
Domain entities - Core business objects
"""
from dataclasses import dataclass
from typing import Literal
import ipaddress


@dataclass(frozen=True)
class VLANEntity:
    """
    Core VLAN entity representing the business domain object.
    Immutable and contains business logic.
    """
    id: int
    name: str
    vlan_id: int
    subnet: str
    gateway: str
    status: Literal["active", "inactive", "maintenance"]
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        """Validate business rules"""
        if not (1 <= self.vlan_id <= 4094):
            raise ValueError(f"VLAN ID {self.vlan_id} must be between 1 and 4094")
        
        try:
            network = ipaddress.ip_network(self.subnet, strict=False)
            gateway = ipaddress.ip_address(self.gateway)
        except ValueError as e:
            raise ValueError(f"Invalid network configuration: {e}")
        
        if gateway not in network:
            raise ValueError(f"Gateway {self.gateway} is not in subnet {self.subnet}")
    
