from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class SearchQuery(BaseModel):
    query: str = Field(..., description="Search query string")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional filters")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Results offset for pagination")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field(default="desc", description="Sort order: asc or desc")

class SearchResult(BaseModel):
    id: str
    type: str  # user, complaint, meeting, project, etc.
    title: str
    content: str
    metadata: Dict[str, Any]
    score: float
    highlights: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[SearchResult]
    took_ms: int
    facets: Optional[Dict[str, Any]] = None

class IndexDocument(BaseModel):
    id: str
    type: str
    title: str
    content: str
    metadata: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SearchStats(BaseModel):
    total_documents: int
    index_size_bytes: int
    search_requests_total: int
    avg_response_time_ms: float
    last_updated: Optional[datetime] = None

# Search filter models
class DateRangeFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class UserSearchFilters(BaseModel):
    sector_id: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    date_range: Optional[DateRangeFilter] = None

class ComplaintSearchFilters(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    sector_id: Optional[str] = None
    date_range: Optional[DateRangeFilter] = None

class MeetingSearchFilters(BaseModel):
    status: Optional[str] = None
    type: Optional[str] = None
    sector_id: Optional[str] = None
    date_range: Optional[DateRangeFilter] = None

class ProjectSearchFilters(BaseModel):
    status: Optional[str] = None
    sector_id: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    date_range: Optional[DateRangeFilter] = None