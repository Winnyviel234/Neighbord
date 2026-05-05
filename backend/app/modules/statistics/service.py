from typing import Dict, Any
from app.modules.statistics.repository import StatisticsRepository

class StatisticsService:
    def __init__(self):
        self.repo = StatisticsRepository()

    async def get_dashboard_overview(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get complete dashboard overview (admin only)"""
        if current_user.get("role_name") not in ["admin", "directiva", "tesorero"]:
            raise Exception("No tienes permisos para ver estadísticas del dashboard")

        return await self.repo.get_dashboard_overview()

    async def get_user_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get user statistics"""
        if current_user.get("role_name") not in ["admin", "directiva", "tesorero"]:
            raise Exception("No tienes permisos para ver estadísticas de usuarios")

        return await self.repo.get_user_statistics()

    async def get_payment_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get payment statistics"""
        if current_user.get("role_name") not in ["admin", "directiva", "tesorero"]:
            raise Exception("No tienes permisos para ver estadísticas de pagos")

        return await self.repo.get_payment_statistics()

    async def get_voting_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get voting statistics"""
        if current_user.get("role_name") not in ["admin", "directiva", "tesorero"]:
            raise Exception("No tienes permisos para ver estadísticas de votaciones")

        return await self.repo.get_voting_statistics()

    async def get_meeting_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get meeting statistics"""
        if current_user.get("role_name") not in ["admin", "directiva", "tesorero"]:
            raise Exception("No tienes permisos para ver estadísticas de reuniones")

        return await self.repo.get_meeting_statistics()

    async def get_complaint_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get complaint statistics"""
        if current_user.get("role_name") not in ["admin", "directiva", "tesorero"]:
            raise Exception("No tienes permisos para ver estadísticas de quejas")

        return await self.repo.get_complaint_statistics()

    async def get_report_analytics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get report analytics payload"""
        if current_user.get("role_name") not in ["admin", "directiva", "tesorero"]:
            raise Exception("No tienes permisos para ver analíticas de reportes")

        return await self.repo.get_report_analytics()

    async def get_chat_statistics(self, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Get chat statistics"""
        if current_user.get("role_name") not in ["admin", "directiva", "tesorero"]:
            raise Exception("No tienes permisos para ver estadísticas de chat")

        return await self.repo.get_chat_statistics()