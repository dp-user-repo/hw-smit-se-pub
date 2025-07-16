"""
API error handlers - Centralized error handling
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.domain.exceptions import (
    VLANNotFoundError,
    VLANConflictError,
    VLANValidationError,
    StorageError
)


def create_error_response(error_code: str, message: str, status_code: int, details: dict = None):
    """Create standardized error response"""
    content = {
        "error": error_code,
        "message": message
    }
    if details:
        content["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def vlan_not_found_handler(request: Request, exc: VLANNotFoundError):
    """Handle VLAN not found errors"""
    return create_error_response(
        error_code="VLAN_NOT_FOUND",
        message=str(exc),
        status_code=status.HTTP_404_NOT_FOUND,
        details={"vlan_id": exc.vlan_id}
    )


async def vlan_conflict_handler(request: Request, exc: VLANConflictError):
    """Handle VLAN conflict errors"""
    return create_error_response(
        error_code="VLAN_CONFLICT",
        message=str(exc),
        status_code=status.HTTP_409_CONFLICT,
        details={"vlan_id": exc.vlan_id}
    )


async def vlan_validation_handler(request: Request, exc: VLANValidationError):
    """Handle VLAN validation errors"""
    return create_error_response(
        error_code="VALIDATION_ERROR",
        message=str(exc),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def storage_error_handler(request: Request, exc: StorageError):
    """Handle storage errors"""
    return create_error_response(
        error_code="STORAGE_ERROR",
        message="Storage system error occurred",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )


async def value_error_handler(request: Request, exc: ValueError):
    """Handle general validation errors"""
    return create_error_response(
        error_code="VALIDATION_ERROR",
        message=str(exc),
        status_code=status.HTTP_400_BAD_REQUEST
    )


async def request_validation_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI request validation errors (422)"""
    return create_error_response(
        error_code="REQUEST_VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"errors": [{"msg": str(err["msg"]), "type": err["type"], "loc": err["loc"]} for err in exc.errors()]}
    )


async def pydantic_validation_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors (422)"""
    return create_error_response(
        error_code="VALIDATION_ERROR",
        message="Data validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"errors": [{"msg": str(err["msg"]), "type": err["type"], "loc": err["loc"]} for err in exc.errors()]}
    )


async def unsupported_media_type_handler(request: Request, exc: Exception):
    """Handle unsupported media type errors (415)"""
    return create_error_response(
        error_code="UNSUPPORTED_MEDIA_TYPE",
        message="Content-Type must be application/json",
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    )


async def payload_too_large_handler(request: Request, exc: Exception):
    """Handle payload too large errors (413)"""
    return create_error_response(
        error_code="PAYLOAD_TOO_LARGE",
        message="Request payload is too large",
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    )


async def method_not_allowed_handler(request: Request, exc: Exception):
    """Handle method not allowed errors (405)"""
    return create_error_response(
        error_code="METHOD_NOT_ALLOWED",
        message="HTTP method not allowed for this endpoint",
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    return create_error_response(
        error_code="INTERNAL_ERROR",
        message="An internal server error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )