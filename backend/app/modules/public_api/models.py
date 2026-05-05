"""
Public API models for limited public access
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PublicSectorInfo(BaseModel):
    """Public sector information"""
    id: str
    name: str
    description: Optional[str]
    location: Optional[str]
    total_users: int
    active_projects: int
    last_activity: Optional[datetime]


class PublicProjectInfo(BaseModel):
    """Public project information"""
    id: str
    title: str
    description: Optional[str]
    sector_id: str
    sector_name: str
    status: str
    progress_percentage: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    budget: Optional[float]
    created_at: datetime


class PublicMeetingInfo(BaseModel):
    """Public meeting information"""
    id: str
    title: str
    description: Optional[str]
    sector_id: str
    sector_name: str
    scheduled_date: datetime
    location: Optional[str]
    meeting_type: str
    status: str
    attendee_count: int


class PublicComplaintInfo(BaseModel):
    """Public complaint information (limited)"""
    id: str
    title: str
    category: str
    sector_id: str
    sector_name: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    is_resolved: bool


class PublicStats(BaseModel):
    """Public statistics"""
    total_sectors: int
    total_users: int
    total_projects: int
    active_projects: int
    total_meetings: int
    upcoming_meetings: int
    total_complaints: int
    resolved_complaints: int
    last_updated: datetime


class APIKeyInfo(BaseModel):
    """API key information"""
    id: str
    name: str
    created_at: datetime
    last_used: Optional[datetime]
    request_count: int
    rate_limit_remaining: int
    expires_at: Optional[datetime]


class PublicAPIResponse(BaseModel):
    """Standard public API response"""
    success: bool
    data: Any
    message: Optional[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str]