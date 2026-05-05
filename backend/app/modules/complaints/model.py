from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class Complaint(BaseModel):
    id: Optional[UUID]
    user_id: UUID
    title: str
    description: str
    category: str = "general"
    priority: str = "media"
    status: str = "abierta"
    assigned_to: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ComplaintCreate(BaseModel):
    title: str
    description: str
    category: str = "general"
    priority: str = "media"

class ComplaintUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[UUID] = None

class ComplaintResponse(BaseModel):
    id: UUID
    user_id: UUID
    user_name: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    assigned_to: Optional[UUID] = None
    assigned_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class ComplaintComment(BaseModel):
    id: Optional[UUID]
    complaint_id: UUID
    user_id: UUID
    comment: str
    created_at: Optional[datetime] = None

class ComplaintCommentCreate(BaseModel):
    comment: str