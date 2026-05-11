from typing import Dict, Any
from fastapi import HTTPException
from app.modules.statistics.repository import StatisticsRepository

ALLOWED_ROLES = ["admin", "directiva", "tesorero"]

def _check_permissions(current_user: Dict[str, Any], resource: str):
    """Check if user has required role, raise 403 HTTPException if not."""
    role = current_user.get("role_name") or current_user.get("rol")
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=403,
            detail=f"No tienes permisos para ver estadísticas de {resource}"
        )

class StatisticsService:
    def __init__(self):
        self.repo = StatisticsRepository()

    async def get_dashboard_overview(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        _check_permissions(current_user, "dashboard")
        return await self.repo.get_dashboard_overview()

    async def get_user_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        _check_permissions(current_user, "usuarios")
        return await self.repo.get_user_statistics()

    async def get_payment_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        _check_permissions(current_user, "pagos")
        return await self.repo.get_payment_statistics()

    async def get_voting_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        _check_permissions(current_user, "votaciones")
        return await self.repo.get_voting_statistics()

    async def get_meeting_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        _check_permissions(current_user, "reuniones")
        return await self.repo.get_meeting_statistics()

    async def get_complaint_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        _check_permissions(current_user, "quejas")
        return await self.repo.get_complaint_statistics()

    async def get_report_analytics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        _check_permissions(current_user, "analíticas")
        return await self.repo.get_report_analytics()

    async def get_chat_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        _check_permissions(current_user, "chat")
        return await self.repo.get_chat_statistics()