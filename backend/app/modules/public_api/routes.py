"""
Public API routes with rate limiting
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.modules.public_api.models import (
    PublicSectorInfo, PublicProjectInfo, PublicMeetingInfo,
    PublicComplaintInfo, PublicStats, APIKeyInfo, PublicAPIResponse
)
from app.modules.public_api.service import public_api_service
from app.core.security import require_role


router = APIRouter(prefix="/public", tags=["public-api"])
limiter = Limiter(key_func=get_remote_address)


async def get_api_key_info(api_key: Optional[str] = Header(None, alias="X-API-Key")) -> Optional[Dict[str, Any]]:
    """Dependency to validate API key"""
    if not api_key:
        return None

    key_info = await public_api_service.validate_api_key(api_key)
    if not key_info:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Update usage stats
    await public_api_service.update_api_key_usage(key_info["id"])

    return key_info


async def check_rate_limit(
    request: Request,
    api_key_info: Optional[Dict[str, Any]] = Depends(get_api_key_info)
) -> None:
    """Check rate limiting for the request"""
    api_key = api_key_info["key"] if api_key_info else None
    endpoint = request.url.path

    allowed = await public_api_service.check_rate_limit(api_key, endpoint)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )


@router.get("/stats", response_model=PublicAPIResponse)
@limiter.limit("10/minute")
async def get_public_stats(
    request: Request,
    rate_limit_check: None = Depends(check_rate_limit)
):
    """Get public community statistics"""
    try:
        stats = await public_api_service.get_public_stats()
        return PublicAPIResponse(
            success=True,
            data=stats,
            message="Public statistics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/sectors", response_model=PublicAPIResponse)
@limiter.limit("20/minute")
async def get_public_sectors(
    request: Request,
    rate_limit_check: None = Depends(check_rate_limit)
):
    """Get public information about community sectors"""
    try:
        sectors = await public_api_service.get_public_sectors()
        return PublicAPIResponse(
            success=True,
            data=sectors,
            message=f"Retrieved {len(sectors)} sectors"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sectors: {str(e)}")


@router.get("/projects", response_model=PublicAPIResponse)
@limiter.limit("30/minute")
async def get_public_projects(
    request: Request,
    sector_id: Optional[str] = None,
    limit: int = 50,
    rate_limit_check: None = Depends(check_rate_limit)
):
    """Get public information about community projects"""
    try:
        if limit > 100:
            limit = 100  # Max limit

        projects = await public_api_service.get_public_projects(sector_id=sector_id, limit=limit)
        return PublicAPIResponse(
            success=True,
            data=projects,
            message=f"Retrieved {len(projects)} public projects"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")


@router.get("/meetings", response_model=PublicAPIResponse)
@limiter.limit("20/minute")
async def get_public_meetings(
    request: Request,
    sector_id: Optional[str] = None,
    upcoming_only: bool = True,
    limit: int = 20,
    rate_limit_check: None = Depends(check_rate_limit)
):
    """Get public information about community meetings"""
    try:
        if limit > 50:
            limit = 50  # Max limit

        meetings = await public_api_service.get_public_meetings(
            sector_id=sector_id,
            upcoming_only=upcoming_only,
            limit=limit
        )
        return PublicAPIResponse(
            success=True,
            data=meetings,
            message=f"Retrieved {len(meetings)} public meetings"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get meetings: {str(e)}")


@router.get("/complaints", response_model=PublicAPIResponse)
@limiter.limit("15/minute")
async def get_public_complaints(
    request: Request,
    sector_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    rate_limit_check: None = Depends(check_rate_limit)
):
    """Get public information about community complaints (limited fields)"""
    try:
        if limit > 50:
            limit = 50  # Max limit

        complaints = await public_api_service.get_public_complaints(
            sector_id=sector_id,
            status=status,
            limit=limit
        )
        return PublicAPIResponse(
            success=True,
            data=complaints,
            message=f"Retrieved {len(complaints)} public complaints"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get complaints: {str(e)}")


# Admin endpoints for API key management
@router.post("/keys", response_model=PublicAPIResponse)
async def create_api_key(
    name: str,
    expires_in_days: Optional[int] = None,
    current_user: dict = Depends(require_role("admin"))
):
    """Create a new API key (Admin only)"""
    try:
        api_key = await public_api_service.create_api_key(name, expires_in_days)
        return PublicAPIResponse(
            success=True,
            data=api_key,
            message="API key created successfully. Save the key value - it won't be shown again."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create API key: {str(e)}")


@router.get("/keys", response_model=PublicAPIResponse)
async def list_api_keys(
    current_user: dict = Depends(require_role("admin"))
):
    """List all API keys (Admin only)"""
    try:
        keys = await public_api_service.list_api_keys()
        return PublicAPIResponse(
            success=True,
            data=keys,
            message=f"Retrieved {len(keys)} API keys"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list API keys: {str(e)}")


@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    """Revoke an API key (Admin only)"""
    try:
        revoked = await public_api_service.revoke_api_key(key_id)
        if not revoked:
            raise HTTPException(status_code=404, detail="API key not found")

        return PublicAPIResponse(
            success=True,
            data=None,
            message="API key revoked successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke API key: {str(e)}")


@router.get("/limits")
async def get_rate_limits(
    request: Request,
    api_key_info: Optional[Dict[str, Any]] = Depends(get_api_key_info)
):
    """Get current rate limit status"""
    api_key = api_key_info["key"] if api_key_info else None

    # This is a simplified response - in production you'd check actual limits
    return PublicAPIResponse(
        success=True,
        data={
            "rate_limit_max": public_api_service.rate_limit_max_requests,
            "rate_limit_window_seconds": public_api_service.rate_limit_window,
            "has_api_key": api_key is not None
        },
        message="Rate limit information"
    )