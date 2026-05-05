from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class AuditLogBase(BaseModel):
    user_id: Optional[UUID] = None
    action: str = Field(..., description="Action performed (CREATE, UPDATE, DELETE, etc.)")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[UUID] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AuditLog(AuditLogBase):
    id: UUID
    timestamp: datetime

class AuditLogCreate(AuditLogBase):
    pass

class UserConsentBase(BaseModel):
    user_id: UUID
    consent_type: str
    consented: bool = True
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class UserConsent(UserConsentBase):
    id: UUID
    consent_date: datetime
    withdrawal_date: Optional[datetime] = None

class UserConsentCreate(UserConsentBase):
    pass

class DataDeletionRequestBase(BaseModel):
    user_id: UUID
    reason: Optional[str] = None
    notes: Optional[str] = None

class DataDeletionRequest(DataDeletionRequestBase):
    id: UUID
    request_date: datetime
    status: str = "pending"
    processed_by: Optional[UUID] = None
    processed_date: Optional[datetime] = None

class DataDeletionRequestCreate(DataDeletionRequestBase):
    pass

class BackupLogBase(BaseModel):
    backup_type: str
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BackupLog(BackupLogBase):
    id: UUID
    status: str = "running"
    started_at: datetime
    completed_at: Optional[datetime] = None

class BackupLogCreate(BackupLogBase):
    pass

# Audit report models
class AuditReportRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[UUID] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)

class AuditSummary(BaseModel):
    total_logs: int
    actions_count: Dict[str, int]
    resource_types_count: Dict[str, int]
    users_count: int
    date_range: Dict[str, datetime]

class GDPRComplianceStatus(BaseModel):
    total_users: int
    users_with_consent: int
    pending_deletion_requests: int
    data_retention_compliant: int
    compliance_percentage: float