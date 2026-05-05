from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user

from .service import SearchService
from .model import (
    SearchResponse, SearchStats, UserSearchFilters,
    ComplaintSearchFilters, MeetingSearchFilters, ProjectSearchFilters
)

router = APIRouter(prefix="/search", tags=["search"])

# Dependency injection
def get_search_service() -> SearchService:
    return SearchService()

@router.get("/", response_model=SearchResponse)
async def search_all(
    q: str = Query(..., description="Search query"),
    type_filter: Optional[str] = Query(None, description="Filter by document type"),
    sector_id: Optional[str] = Query(None, description="Filter by sector"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset"),
    current_user: dict = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """Search across all indexed documents"""
    filters = {}

    if type_filter:
        filters["type"] = type_filter

    if sector_id:
        # Add sector filtering based on user permissions
        user_sector = current_user.get("sector_id")
        if user_sector and str(user_sector) != sector_id:
            # Users can only search within their sector unless they have broader permissions
            if "admin" not in current_user.get("role_permissions", []):
                filters["metadata.sector_id"] = str(user_sector)
        else:
            filters["metadata.sector_id"] = sector_id

    return await search_service.search(q, filters, limit, offset)

@router.get("/users", response_model=SearchResponse)
async def search_users(
    q: str = Query(..., description="Search query"),
    sector_id: Optional[str] = Query(None, description="Filter by sector"),
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: dict = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """Search users"""
    filters = UserSearchFilters(
        sector_id=sector_id,
        role=role,
        status=status
    )

    # Apply sector restrictions for non-admin users
    if "admin" not in current_user.get("role_permissions", []):
        user_sector = current_user.get("sector_id")
        if user_sector:
            filters.sector_id = str(user_sector)

    return await search_service.search_users(q, filters, limit)

@router.get("/complaints", response_model=SearchResponse)
async def search_complaints(
    q: str = Query(..., description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned user"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: dict = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """Search complaints"""
    filters = ComplaintSearchFilters(
        status=status,
        priority=priority,
        assigned_to=assigned_to
    )

    # Apply sector restrictions for non-admin users
    if "admin" not in current_user.get("role_permissions", []):
        user_sector = current_user.get("sector_id")
        if user_sector:
            filters.sector_id = str(user_sector)

    return await search_service.search_complaints(q, filters, limit)

@router.get("/meetings", response_model=SearchResponse)
async def search_meetings(
    q: str = Query(..., description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    meeting_type: Optional[str] = Query(None, description="Filter by meeting type"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: dict = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """Search meetings"""
    filters = MeetingSearchFilters(
        status=status,
        type=meeting_type
    )

    # Apply sector restrictions for non-admin users
    if "admin" not in current_user.get("role_permissions", []):
        user_sector = current_user.get("sector_id")
        if user_sector:
            filters.sector_id = str(user_sector)

    return await search_service.search_meetings(q, filters, limit)

@router.get("/projects", response_model=SearchResponse)
async def search_projects(
    q: str = Query(..., description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    budget_min: Optional[float] = Query(None, description="Minimum budget"),
    budget_max: Optional[float] = Query(None, description="Maximum budget"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: dict = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """Search projects"""
    filters = ProjectSearchFilters(
        status=status,
        budget_min=budget_min,
        budget_max=budget_max
    )

    # Apply sector restrictions for non-admin users
    if "admin" not in current_user.get("role_permissions", []):
        user_sector = current_user.get("sector_id")
        if user_sector:
            filters.sector_id = str(user_sector)

    return await search_service.search_projects(q, filters, limit)

@router.get("/stats", response_model=SearchStats)
async def get_search_stats(
    current_user: dict = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """Get search statistics"""
    # Only admins can see search stats
    if "admin" not in current_user.get("role_permissions", []):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not authorized to view search statistics")

    return await search_service.get_search_stats()

@router.post("/reindex")
async def reindex_all_documents(
    current_user: dict = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """Reindex all documents (admin only)"""
    if "admin" not in current_user.get("role_permissions", []):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not authorized to reindex documents")

    # This would trigger a background job to reindex all documents
    # For now, just initialize the index
    success = await search_service.initialize_search_index()

    return {
        "message": "Reindexing initiated" if success else "Search is disabled",
        "success": success
    }
