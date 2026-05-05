from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import logging
from fastapi import Request

from .repository import AuditRepository
from .model import (
    AuditLogCreate, UserConsentCreate, DataDeletionRequestCreate,
    BackupLogCreate, AuditReportRequest, AuditSummary, GDPRComplianceStatus
)

logger = logging.getLogger(__name__)

class AuditService:
    def __init__(self, repository: AuditRepository):
        self.repo = repository

    async def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an auditable action"""
        try:
            ip_address = None
            user_agent = None

            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")

            audit_data = AuditLogCreate(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata
            )

            await self.repo.create_audit_log(audit_data)

            # Also log to application logger
            logger.info(f"AUDIT: {action} on {resource_type} by user {user_id}")

        except Exception as e:
            logger.error(f"Failed to log audit action: {e}")

    async def get_audit_logs(self, report_request: AuditReportRequest) -> List[Dict[str, Any]]:
        """Get audit logs with filtering"""
        logs = await self.repo.get_audit_logs(
            start_date=report_request.start_date,
            end_date=report_request.end_date,
            user_id=report_request.user_id,
            action=report_request.action,
            resource_type=report_request.resource_type,
            limit=report_request.limit
        )
        return [log.model_dump() for log in logs]

    async def get_audit_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> AuditSummary:
        """Get audit summary statistics"""
        summary_data = await self.repo.get_audit_summary(start_date, end_date)
        return AuditSummary(**summary_data)

    # User Consent Management
    async def record_user_consent(
        self,
        user_id: UUID,
        consent_type: str,
        consented: bool = True,
        request: Optional[Request] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record user consent for GDPR compliance"""
        ip_address = request.client.host if request and request.client else None
        user_agent = request.headers.get("user-agent") if request else None

        consent_data = UserConsentCreate(
            user_id=user_id,
            consent_type=consent_type,
            consented=consented,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata
        )

        consent = await self.repo.create_user_consent(consent_data)

        # Log the consent action
        await self.log_action(
            action="CONSENT_GIVEN" if consented else "CONSENT_WITHDRAWN",
            resource_type="user_consents",
            resource_id=consent.id,
            user_id=user_id,
            new_values={"consent_type": consent_type, "consented": consented},
            request=request
        )

        return consent.model_dump()

    async def get_user_consents(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get all consents for a user"""
        consents = await self.repo.get_user_consents(user_id)
        return [consent.model_dump() for consent in consents]

    async def withdraw_consent(self, user_id: UUID, consent_type: str, request: Optional[Request] = None) -> bool:
        """Withdraw user consent"""
        # Find the consent record
        consents = await self.repo.get_user_consents(user_id)
        consent_record = next((c for c in consents if c.consent_type == consent_type), None)

        if consent_record:
            await self.repo.update_consent(consent_record.id, False)

            # Log the withdrawal
            await self.log_action(
                action="CONSENT_WITHDRAWN",
                resource_type="user_consents",
                resource_id=consent_record.id,
                user_id=user_id,
                old_values={"consented": True},
                new_values={"consented": False},
                request=request
            )
            return True
        return False

    # Data Deletion (Right to be Forgotten)
    async def request_data_deletion(
        self,
        user_id: UUID,
        reason: Optional[str] = None,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """Request data deletion for GDPR compliance"""
        deletion_data = DataDeletionRequestCreate(
            user_id=user_id,
            reason=reason
        )

        deletion_request = await self.repo.create_deletion_request(deletion_data)

        # Log the deletion request
        await self.log_action(
            action="DATA_DELETION_REQUESTED",
            resource_type="data_deletion_requests",
            resource_id=deletion_request.id,
            user_id=user_id,
            new_values={"reason": reason},
            request=request
        )

        return deletion_request.model_dump()

    async def process_data_deletion(
        self,
        request_id: UUID,
        approved: bool,
        processed_by: UUID,
        notes: Optional[str] = None,
        request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """Process a data deletion request"""
        status = "approved" if approved else "rejected"

        deletion_request = await self.repo.update_deletion_request(
            request_id, status, processed_by, notes
        )

        # Log the processing
        await self.log_action(
            action="DATA_DELETION_PROCESSED",
            resource_type="data_deletion_requests",
            resource_id=request_id,
            user_id=processed_by,
            old_values={"status": "pending"},
            new_values={"status": status, "notes": notes},
            request=request
        )

        if approved:
            # TODO: Implement actual data deletion/anonymization
            # This would involve updating user data to anonymize PII
            pass

        return deletion_request.model_dump()

    async def get_pending_deletion_requests(self) -> List[Dict[str, Any]]:
        """Get pending data deletion requests"""
        requests = await self.repo.get_deletion_requests("pending")
        return [req.model_dump() for req in requests]

    # Backup Management
    async def start_backup(self, backup_type: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start a backup operation"""
        backup_data = BackupLogCreate(
            backup_type=backup_type,
            metadata=metadata
        )

        backup_log = await self.repo.create_backup_log(backup_data)

        logger.info(f"Backup started: {backup_type} (ID: {backup_log.id})")

        return backup_log.model_dump()

    async def complete_backup(
        self,
        backup_id: UUID,
        success: bool,
        file_path: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete a backup operation"""
        status = "completed" if success else "failed"

        backup_log = await self.repo.update_backup_log(
            backup_id, status, file_path, file_size_bytes, error_message
        )

        logger.info(f"Backup completed: {status} (ID: {backup_id})")

        return backup_log.model_dump()

    async def get_backup_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get backup history"""
        backups = await self.repo.get_backup_logs(limit)
        return [backup.model_dump() for backup in backups]

    # GDPR Compliance Reporting
    async def get_gdpr_compliance_status(self) -> GDPRComplianceStatus:
        """Get GDPR compliance status"""
        status_data = await self.repo.get_gdpr_compliance_status()
        return GDPRComplianceStatus(**status_data)