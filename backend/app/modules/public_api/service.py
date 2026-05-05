"""
Public API service with rate limiting and API key management
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException

from app.core.cache.redis_cache import cache_manager
from app.core.supabase import table
from app.modules.public_api.models import (
    PublicSectorInfo, PublicProjectInfo, PublicMeetingInfo,
    PublicComplaintInfo, PublicStats, APIKeyInfo
)


class PublicAPIService:
    """Service for public API operations with rate limiting"""

    def __init__(self):
        self.rate_limit_window = 3600  # 1 hour in seconds
        self.rate_limit_max_requests = 100  # requests per hour for public API

    async def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return key info"""
        if not api_key:
            return None

        # Check cache first
        cache_key = f"api_key:{api_key}"
        cached_key = await cache_manager.get(cache_key)

        if cached_key:
            return cached_key

        # Check database
        result = table("api_keys").select("*").eq("key", api_key).eq("active", True).execute()

        if not result.data:
            return None

        key_data = result.data[0]

        # Check expiration
        if key_data.get("expires_at"):
            expires_at = datetime.fromisoformat(key_data["expires_at"].replace('Z', '+00:00'))
            if datetime.utcnow() > expires_at:
                return None

        # Cache valid key for 5 minutes
        await cache_manager.set(cache_key, key_data, ttl=300)

        return key_data

    async def check_rate_limit(self, api_key: str, endpoint: str) -> bool:
        """Check if request is within rate limits"""
        if not cache_manager.enabled:
            return True  # Allow if no Redis

        # Use API key or IP-based limiting
        identifier = api_key or "anonymous"
        window_key = f"rate_limit:{identifier}:{endpoint}:{int(datetime.utcnow().timestamp() / self.rate_limit_window)}"

        current_count = await cache_manager.get(window_key) or 0

        if current_count >= self.rate_limit_max_requests:
            return False

        # Increment counter
        await cache_manager.set(window_key, current_count + 1, ttl=self.rate_limit_window)
        return True

    async def update_api_key_usage(self, api_key_id: str) -> None:
        """Update API key usage statistics"""
        try:
            # Update last_used and increment request_count
            table("api_keys").update({
                "last_used": datetime.utcnow().isoformat(),
                "request_count": table.rpc("increment", {"table_name": "api_keys", "id": api_key_id, "column_name": "request_count"})
            }).eq("id", api_key_id).execute()
        except Exception:
            # Don't fail the request if stats update fails
            pass

    async def get_public_sectors(self) -> List[PublicSectorInfo]:
        """Get public sector information"""
        # Get sectors with basic stats
        result = table.rpc("get_public_sectors").execute()

        sectors = []
        for item in result.data:
            sectors.append(PublicSectorInfo(**item))

        return sectors

    async def get_public_projects(self, sector_id: Optional[str] = None, limit: int = 50) -> List[PublicProjectInfo]:
        """Get public project information"""
        query = table("projects").select("""
            id, title, description, sector_id, status, progress_percentage,
            start_date, end_date, budget, created_at,
            sectors(name)
        """).eq("is_public", True)

        if sector_id:
            query = query.eq("sector_id", sector_id)

        result = query.limit(limit).execute()

        projects = []
        for item in result.data:
            projects.append(PublicProjectInfo(
                id=item["id"],
                title=item["title"],
                description=item["description"],
                sector_id=item["sector_id"],
                sector_name=item["sectors"]["name"] if item["sectors"] else "Unknown",
                status=item["status"],
                progress_percentage=item["progress_percentage"] or 0,
                start_date=item.get("start_date"),
                end_date=item.get("end_date"),
                budget=item.get("budget"),
                created_at=item["created_at"]
            ))

        return projects

    async def get_public_meetings(self, sector_id: Optional[str] = None, upcoming_only: bool = True, limit: int = 20) -> List[PublicMeetingInfo]:
        """Get public meeting information"""
        query = table("meetings").select("""
            id, title, description, sector_id, scheduled_date, location,
            meeting_type, status, created_at,
            sectors(name)
        """).eq("is_public", True)

        if sector_id:
            query = query.eq("sector_id", sector_id)

        if upcoming_only:
            query = query.gte("scheduled_date", datetime.utcnow().isoformat())

        result = query.order("scheduled_date").limit(limit).execute()

        meetings = []
        for item in result.data:
            # Get attendee count
            attendee_result = table("meeting_attendees").select("id", count="exact").eq("meeting_id", item["id"]).execute()
            attendee_count = attendee_result.count or 0

            meetings.append(PublicMeetingInfo(
                id=item["id"],
                title=item["title"],
                description=item["description"],
                sector_id=item["sector_id"],
                sector_name=item["sectors"]["name"] if item["sectors"] else "Unknown",
                scheduled_date=item["scheduled_date"],
                location=item.get("location"),
                meeting_type=item["meeting_type"],
                status=item["status"],
                attendee_count=attendee_count
            ))

        return meetings

    async def get_public_complaints(self, sector_id: Optional[str] = None, status: Optional[str] = None, limit: int = 20) -> List[PublicComplaintInfo]:
        """Get public complaint information (limited fields)"""
        query = table("complaints").select("""
            id, title, category, sector_id, status, priority,
            created_at, updated_at,
            sectors(name)
        """).eq("is_public", True)

        if sector_id:
            query = query.eq("sector_id", sector_id)

        if status:
            query = query.eq("status", status)

        result = query.order("created_at", desc=True).limit(limit).execute()

        complaints = []
        for item in result.data:
            complaints.append(PublicComplaintInfo(
                id=item["id"],
                title=item["title"],
                category=item["category"],
                sector_id=item["sector_id"],
                sector_name=item["sectors"]["name"] if item["sectors"] else "Unknown",
                status=item["status"],
                priority=item["priority"],
                created_at=item["created_at"],
                updated_at=item["updated_at"],
                is_resolved=item["status"] in ["resolved", "closed"]
            ))

        return complaints

    async def get_public_stats(self) -> PublicStats:
        """Get public statistics"""
        # Use cached stats if available
        cache_key = "public_stats"
        cached_stats = await cache_manager.get(cache_key)

        if cached_stats:
            return PublicStats(**cached_stats)

        # Calculate stats
        sectors_result = table("sectors").select("id", count="exact").execute()
        users_result = table("users").select("id", count="exact").execute()
        projects_result = table("projects").select("id", count="exact").execute()
        active_projects_result = table("projects").select("id", count="exact").eq("status", "active").execute()
        meetings_result = table("meetings").select("id", count="exact").execute()
        upcoming_meetings_result = table("meetings").select("id", count="exact").gte("scheduled_date", datetime.utcnow().isoformat()).execute()
        complaints_result = table("complaints").select("id", count="exact").execute()
        resolved_complaints_result = table("complaints").select("id", count="exact").in_("status", ["resolved", "closed"]).execute()

        stats = PublicStats(
            total_sectors=sectors_result.count or 0,
            total_users=users_result.count or 0,
            total_projects=projects_result.count or 0,
            active_projects=active_projects_result.count or 0,
            total_meetings=meetings_result.count or 0,
            upcoming_meetings=upcoming_meetings_result.count or 0,
            total_complaints=complaints_result.count or 0,
            resolved_complaints=resolved_complaints_result.count or 0,
            last_updated=datetime.utcnow()
        )

        # Cache for 10 minutes
        await cache_manager.set(cache_key, stats.dict(), ttl=600)

        return stats

    async def create_api_key(self, name: str, expires_in_days: Optional[int] = None) -> APIKeyInfo:
        """Create a new API key (admin only)"""
        api_key = secrets.token_urlsafe(32)
        expires_at = None

        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        key_data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "key": api_key,
            "active": True,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None,
            "request_count": 0
        }

        result = table("api_keys").insert(key_data).execute()

        return APIKeyInfo(**result.data[0])

    async def list_api_keys(self) -> List[APIKeyInfo]:
        """List all API keys (admin only)"""
        result = table("api_keys").select("*").execute()

        keys = []
        for item in result.data:
            keys.append(APIKeyInfo(**item))

        return keys

    async def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key (admin only)"""
        result = table("api_keys").update({"active": False}).eq("id", key_id).execute()
        return len(result.data) > 0


# Global public API service instance
public_api_service = PublicAPIService()