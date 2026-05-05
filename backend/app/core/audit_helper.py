# Audit helper functions for easy integration in other modules
# Import this in services that need audit logging

from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

class AuditHelper:
    def __init__(self):
        self._audit_service = None

    async def get_audit_service(self):
        """Lazy load audit service"""
        if self._audit_service is None:
            from app.modules.audit.service import AuditService
            from app.modules.audit.repository import AuditRepository
            self._audit_service = AuditService(AuditRepository())
        return self._audit_service

    async def log_create(
        self,
        resource_type: str,
        resource_id: UUID,
        new_values: Dict[str, Any],
        user_id: Optional[UUID] = None,
        request: Optional[Request] = None
    ):
        """Log resource creation"""
        audit_service = await self.get_audit_service()
        await audit_service.log_action(
            action="CREATE",
            resource_type=resource_type,
            resource_id=resource_id,
            new_values=new_values,
            user_id=user_id,
            request=request
        )

    async def log_update(
        self,
        resource_type: str,
        resource_id: UUID,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        user_id: Optional[UUID] = None,
        request: Optional[Request] = None
    ):
        """Log resource update"""
        audit_service = await self.get_audit_service()
        await audit_service.log_action(
            action="UPDATE",
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            user_id=user_id,
            request=request
        )

    async def log_delete(
        self,
        resource_type: str,
        resource_id: UUID,
        old_values: Optional[Dict[str, Any]] = None,
        user_id: Optional[UUID] = None,
        request: Optional[Request] = None
    ):
        """Log resource deletion"""
        audit_service = await self.get_audit_service()
        await audit_service.log_action(
            action="DELETE",
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            user_id=user_id,
            request=request
        )

    async def log_login(
        self,
        user_id: UUID,
        request: Optional[Request] = None
    ):
        """Log user login"""
        audit_service = await self.get_audit_service()
        await audit_service.log_action(
            action="LOGIN",
            resource_type="users",
            resource_id=user_id,
            user_id=user_id,
            request=request
        )

    async def log_logout(
        self,
        user_id: UUID,
        request: Optional[Request] = None
    ):
        """Log user logout"""
        audit_service = await self.get_audit_service()
        await audit_service.log_action(
            action="LOGOUT",
            resource_type="users",
            resource_id=user_id,
            user_id=user_id,
            request=request
        )

    async def log_permission_denied(
        self,
        resource_type: str,
        action: str,
        user_id: Optional[UUID] = None,
        request: Optional[Request] = None
    ):
        """Log permission denied attempts"""
        audit_service = await self.get_audit_service()
        await audit_service.log_action(
            action=f"PERMISSION_DENIED_{action.upper()}",
            resource_type=resource_type,
            user_id=user_id,
            request=request,
            metadata={"denied_action": action}
        )

# Global audit helper instance
audit_helper = AuditHelper()

# Convenience functions for easy importing
async def audit_create(*args, **kwargs):
    return await audit_helper.log_create(*args, **kwargs)

async def audit_update(*args, **kwargs):
    return await audit_helper.log_update(*args, **kwargs)

async def audit_delete(*args, **kwargs):
    return await audit_helper.log_delete(*args, **kwargs)

async def audit_login(*args, **kwargs):
    return await audit_helper.log_login(*args, **kwargs)

async def audit_logout(*args, **kwargs):
    return await audit_helper.log_logout(*args, **kwargs)

async def audit_permission_denied(*args, **kwargs):
    return await audit_helper.log_permission_denied(*args, **kwargs)