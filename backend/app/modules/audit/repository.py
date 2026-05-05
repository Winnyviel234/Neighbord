from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.core.supabase import table
from .model import (
    AuditLog, AuditLogCreate, UserConsent, UserConsentCreate,
    DataDeletionRequest, DataDeletionRequestCreate, BackupLog, BackupLogCreate
)

class AuditRepository:
    def __init__(self):
        self.audit_table = table("audit_logs")
        self.consent_table = table("user_consents")
        self.deletion_table = table("data_deletion_requests")
        self.backup_table = table("backup_logs")

    # Audit Logs
    async def create_audit_log(self, audit_data: AuditLogCreate) -> AuditLog:
        data = audit_data.model_dump()
        result = self.audit_table.insert(data).execute()
        return AuditLog(**result.data[0])

    async def get_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        query = self.audit_table.select("*").order("timestamp", desc=True).limit(limit)

        if start_date:
            query = query.gte("timestamp", start_date.isoformat())
        if end_date:
            query = query.lte("timestamp", end_date.isoformat())
        if user_id:
            query = query.eq("user_id", str(user_id))
        if action:
            query = query.eq("action", action)
        if resource_type:
            query = query.eq("resource_type", resource_type)

        result = query.execute()
        return [AuditLog(**item) for item in result.data]

    async def get_audit_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        # Get total count
        query = self.audit_table.select("*", count="exact")
        if start_date:
            query = query.gte("timestamp", start_date.isoformat())
        if end_date:
            query = query.lte("timestamp", end_date.isoformat())

        result = query.execute()
        total_logs = result.count or 0

        # Get actions count
        actions_result = self.audit_table.select("action").execute()
        actions_count = {}
        for item in actions_result.data:
            action = item["action"]
            actions_count[action] = actions_count.get(action, 0) + 1

        # Get resource types count
        resource_result = self.audit_table.select("resource_type").execute()
        resource_types_count = {}
        for item in resource_result.data:
            rt = item["resource_type"]
            resource_types_count[rt] = resource_types_count.get(rt, 0) + 1

        # Get unique users count
        users_result = self.audit_table.select("user_id").execute()
        unique_users = set()
        for item in users_result.data:
            if item["user_id"]:
                unique_users.add(item["user_id"])

        return {
            "total_logs": total_logs,
            "actions_count": actions_count,
            "resource_types_count": resource_types_count,
            "users_count": len(unique_users),
            "date_range": {
                "start": start_date or datetime.min,
                "end": end_date or datetime.max
            }
        }

    # User Consents
    async def create_user_consent(self, consent_data: UserConsentCreate) -> UserConsent:
        data = consent_data.model_dump()
        result = self.consent_table.insert(data).execute()
        return UserConsent(**result.data[0])

    async def get_user_consents(self, user_id: UUID) -> List[UserConsent]:
        result = self.consent_table.select("*").eq("user_id", str(user_id)).execute()
        return [UserConsent(**item) for item in result.data]

    async def update_consent(self, consent_id: UUID, consented: bool) -> UserConsent:
        result = self.consent_table.update({
            "consented": consented,
            "withdrawal_date": datetime.now() if not consented else None
        }).eq("id", str(consent_id)).execute()
        return UserConsent(**result.data[0])

    # Data Deletion Requests
    async def create_deletion_request(self, request_data: DataDeletionRequestCreate) -> DataDeletionRequest:
        data = request_data.model_dump()
        result = self.deletion_table.insert(data).execute()
        return DataDeletionRequest(**result.data[0])

    async def get_deletion_requests(self, status: Optional[str] = None) -> List[DataDeletionRequest]:
        query = self.deletion_table.select("*").order("request_date", desc=True)
        if status:
            query = query.eq("status", status)
        result = query.execute()
        return [DataDeletionRequest(**item) for item in result.data]

    async def update_deletion_request(
        self,
        request_id: UUID,
        status: str,
        processed_by: Optional[UUID] = None,
        notes: Optional[str] = None
    ) -> DataDeletionRequest:
        update_data = {
            "status": status,
            "processed_date": datetime.now()
        }
        if processed_by:
            update_data["processed_by"] = str(processed_by)
        if notes:
            update_data["notes"] = notes

        result = self.deletion_table.update(update_data).eq("id", str(request_id)).execute()
        return DataDeletionRequest(**result.data[0])

    # Backup Logs
    async def create_backup_log(self, backup_data: BackupLogCreate) -> BackupLog:
        data = backup_data.model_dump()
        result = self.backup_table.insert(data).execute()
        return BackupLog(**result.data[0])

    async def update_backup_log(
        self,
        backup_id: UUID,
        status: str,
        file_path: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> BackupLog:
        update_data = {
            "status": status,
            "completed_at": datetime.now()
        }
        if file_path:
            update_data["file_path"] = file_path
        if file_size_bytes:
            update_data["file_size_bytes"] = file_size_bytes
        if error_message:
            update_data["error_message"] = error_message

        result = self.backup_table.update(update_data).eq("id", str(backup_id)).execute()
        return BackupLog(**result.data[0])

    async def get_backup_logs(self, limit: int = 50) -> List[BackupLog]:
        result = self.backup_table.select("*").order("started_at", desc=True).limit(limit).execute()
        return [BackupLog(**item) for item in result.data]

    # GDPR Compliance Status
    async def get_gdpr_compliance_status(self) -> Dict[str, Any]:
        # Total users
        users_result = table("usuarios").select("*", count="exact").execute()
        total_users = users_result.count or 0

        # Users with consent
        consent_result = table("usuarios").select("*", count="exact").eq("gdpr_consent_given", True).execute()
        users_with_consent = consent_result.count or 0

        # Pending deletion requests
        deletion_result = self.deletion_table.select("*", count="exact").eq("status", "pending").execute()
        pending_deletion = deletion_result.count or 0

        # Data retention compliant (users whose retention period hasn't expired)
        retention_result = table("usuarios").select("*", count="exact").gt("data_retention_until", datetime.now().date()).execute()
        retention_compliant = retention_result.count or 0

        compliance_percentage = (users_with_consent / total_users * 100) if total_users > 0 else 0

        return {
            "total_users": total_users,
            "users_with_consent": users_with_consent,
            "pending_deletion_requests": pending_deletion,
            "data_retention_compliant": retention_compliant,
            "compliance_percentage": round(compliance_percentage, 2)
        }