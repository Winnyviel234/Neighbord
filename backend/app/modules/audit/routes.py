from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.security import get_current_user, require_permissions

from .service import AuditService
from .model import AuditReportRequest, AuditSummary, GDPRComplianceStatus

router = APIRouter(prefix="/audit", tags=["audit"])

# Dependency injection
def get_audit_service() -> AuditService:
    from .repository import AuditRepository
    return AuditService(AuditRepository())

@router.get("/logs", response_model=List[dict])
async def get_audit_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[UUID] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(require_permissions(["view_audit_logs"])),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Get audit logs with filtering"""
    report_request = AuditReportRequest(
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        limit=limit
    )

    return await audit_service.get_audit_logs(report_request)

@router.get("/summary", response_model=AuditSummary)
async def get_audit_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(require_permissions(["view_audit_logs"])),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Get audit summary statistics"""
    return await audit_service.get_audit_summary(start_date, end_date)

@router.post("/consent")
async def record_user_consent(
    consent_type: str,
    consented: bool = True,
    request: Request = None,
    current_user: dict = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Record user consent for GDPR compliance"""
    return await audit_service.record_user_consent(
        user_id=current_user["id"],
        consent_type=consent_type,
        consented=consented,
        request=request
    )

@router.get("/consent", response_model=List[dict])
async def get_user_consents(
    current_user: dict = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Get user's consents"""
    return await audit_service.get_user_consents(current_user["id"])

@router.delete("/consent/{consent_type}")
async def withdraw_consent(
    consent_type: str,
    request: Request = None,
    current_user: dict = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Withdraw user consent"""
    success = await audit_service.withdraw_consent(
        user_id=current_user["id"],
        consent_type=consent_type,
        request=request
    )

    if not success:
        raise HTTPException(status_code=404, detail="Consent record not found")

    return {"message": "Consent withdrawn successfully"}

@router.post("/data-deletion")
async def request_data_deletion(
    reason: Optional[str] = None,
    request: Request = None,
    current_user: dict = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Request data deletion (GDPR right to be forgotten)"""
    return await audit_service.request_data_deletion(
        user_id=current_user["id"],
        reason=reason,
        request=request
    )

@router.get("/data-deletion/pending", response_model=List[dict])
async def get_pending_deletion_requests(
    current_user: dict = Depends(require_permissions(["manage_data_deletion"])),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Get pending data deletion requests (admin only)"""
    return await audit_service.get_pending_deletion_requests()

@router.put("/data-deletion/{request_id}")
async def process_data_deletion(
    request_id: UUID,
    approved: bool,
    notes: Optional[str] = None,
    request: Request = None,
    current_user: dict = Depends(require_permissions(["manage_data_deletion"])),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Process a data deletion request (admin only)"""
    return await audit_service.process_data_deletion(
        request_id=request_id,
        approved=approved,
        processed_by=current_user["id"],
        notes=notes,
        request=request
    )

@router.get("/backups", response_model=List[dict])
async def get_backup_history(
    limit: int = 50,
    current_user: dict = Depends(require_permissions(["view_backups"])),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Get backup history"""
    return await audit_service.get_backup_history(limit)

@router.get("/gdpr-compliance", response_model=GDPRComplianceStatus)
async def get_gdpr_compliance_status(
    current_user: dict = Depends(require_permissions(["view_compliance"])),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Get GDPR compliance status"""
    return await audit_service.get_gdpr_compliance_status()

# Helper endpoint to log actions from other modules
@router.post("/log")
async def log_audit_action(
    action: str,
    resource_type: str,
    resource_id: Optional[UUID] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    metadata: Optional[dict] = None,
    request: Request = None,
    current_user: dict = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Manually log an audit action (for internal use)"""
    await audit_service.log_action(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=current_user["id"],
        old_values=old_values,
        new_values=new_values,
        request=request,
        metadata=metadata
    )
    return {"message": "Audit log created"}