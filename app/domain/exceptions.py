"""
Domain exceptions - Business logic errors
"""


class VLANDomainException(Exception):
    """Base exception for VLAN domain errors"""
    pass


class VLANNotFoundError(VLANDomainException):
    """VLAN not found error"""
    def __init__(self, vlan_id: int):
        self.vlan_id = vlan_id
        super().__init__(f"VLAN with ID {vlan_id} not found")


class VLANConflictError(VLANDomainException):
    """VLAN conflict error (duplicate VLAN ID)"""
    def __init__(self, vlan_id: int):
        self.vlan_id = vlan_id
        super().__init__(f"VLAN with VLAN ID {vlan_id} already exists")


class VLANValidationError(VLANDomainException):
    """VLAN validation error"""
    pass


class StorageError(VLANDomainException):
    """Storage system error"""
    pass