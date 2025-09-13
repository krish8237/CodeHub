from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.execution import (
    CodeExecutionRequest,
    ExecutionResult,
    LanguageInfo,
    ValidationRequest,
    ValidationResult
)
from app.services.execution import execution_service

router = APIRouter()
security = HTTPBearer()


@router.post("/execute", response_model=ExecutionResult)
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """Execute code with test cases in a secure environment."""
    try:
        result = await execution_service.execute_code(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code execution failed: {str(e)}"
        )


@router.post("/validate", response_model=ValidationResult)
async def validate_syntax(
    request: ValidationRequest,
    current_user: User = Depends(get_current_user)
):
    """Validate code syntax without execution."""
    try:
        result = await execution_service.validate_syntax(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Syntax validation failed: {str(e)}"
        )


@router.get("/languages", response_model=List[LanguageInfo])
async def get_supported_languages(
    current_user: User = Depends(get_current_user)
):
    """Get information about supported programming languages."""
    try:
        return execution_service.get_supported_languages()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get language information: {str(e)}"
        )


@router.post("/build-images")
async def build_docker_images(
    current_user: User = Depends(get_current_user)
):
    """Build Docker images for code execution (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can build Docker images"
        )
    
    try:
        await execution_service.build_docker_images()
        return {"message": "Docker images built successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build Docker images: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_containers(
    current_user: User = Depends(get_current_user)
):
    """Clean up orphaned containers (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can cleanup containers"
        )
    
    try:
        execution_service.cleanup_containers()
        return {"message": "Container cleanup completed"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Container cleanup failed: {str(e)}"
        )