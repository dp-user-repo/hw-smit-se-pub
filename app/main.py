"""
Main application - Clean architecture with design patterns
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import yaml

from app.api.routes import router
from app.api.error_handlers import (
    vlan_not_found_handler,
    vlan_conflict_handler,
    vlan_validation_handler,
    storage_error_handler,
    value_error_handler,
    request_validation_handler,
    pydantic_validation_handler,
    unsupported_media_type_handler,
    payload_too_large_handler,
    method_not_allowed_handler,
    general_exception_handler
)
from app.domain.exceptions import (
    VLANNotFoundError,
    VLANConflictError,
    VLANValidationError,
    StorageError
)
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from pydantic import ValidationError


def create_app() -> FastAPI:
    """Application factory pattern"""

    # Load static OpenAPI spec
    with open("openapi.yml") as f:
        openapi_schema = yaml.safe_load(f)

    app = FastAPI(
        title="VLAN Management API",
        description="REST API for managing VLANs in network infrastructure",
        version="1.0.0"
    )

    # Note: This project creates OpenAPI spec from static openapi.yml 
    # (assignment requirement, design-first approach)
    #
    # To use auto-generated OpenAPI (available at /docs, code-first approach) comment the next line 
    # (and loading static OpenAPI spec above)
    app.openapi_schema = openapi_schema

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    # Register routes
    app.include_router(router)
    
    # Register error handlers (order matters - specific before general)
    app.add_exception_handler(VLANNotFoundError, vlan_not_found_handler)
    app.add_exception_handler(VLANConflictError, vlan_conflict_handler)
    app.add_exception_handler(VLANValidationError, vlan_validation_handler)
    app.add_exception_handler(StorageError, storage_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    
    # HTTP exception handlers
    def handle_http_exceptions(request, exc):
        if exc.status_code == 415:
            return unsupported_media_type_handler(request, exc)
        elif exc.status_code == 413:
            return payload_too_large_handler(request, exc)
        elif exc.status_code == 405:
            return method_not_allowed_handler(request, exc)
        elif exc.status_code == 503:
            # Handle 503 Service Unavailable for health check
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=503,
                content=exc.detail
            )
        raise exc
    
    app.add_exception_handler(HTTPException, handle_http_exceptions)
    app.add_exception_handler(Exception, general_exception_handler)
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)