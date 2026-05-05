from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.modules.statistics.service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["statistics"])

statistics_service = StatisticsService()

@router.get("/dashboard")
async def get_dashboard_overview(user: dict = Depends(get_current_user)):
    """Get complete dashboard overview (admin/directiva/tesorero only)"""
    return await statistics_service.get_dashboard_overview(user)

@router.get("/users")
async def get_user_statistics(user: dict = Depends(get_current_user)):
    """Get user statistics (admin/directiva/tesorero only)"""
    return await statistics_service.get_user_statistics(user)

@router.get("/payments")
async def get_payment_statistics(user: dict = Depends(get_current_user)):
    """Get payment statistics (admin/directiva/tesorero only)"""
    return await statistics_service.get_payment_statistics(user)

@router.get("/votings")
async def get_voting_statistics(user: dict = Depends(get_current_user)):
    """Get voting statistics (admin/directiva/tesorero only)"""
    return await statistics_service.get_voting_statistics(user)

@router.get("/meetings")
async def get_meeting_statistics(user: dict = Depends(get_current_user)):
    """Get meeting statistics (admin/directiva/tesorero only)"""
    return await statistics_service.get_meeting_statistics(user)

@router.get("/complaints")
async def get_complaint_statistics(user: dict = Depends(get_current_user)):
    """Get complaint statistics (admin/directiva/tesorero only)"""
    return await statistics_service.get_complaint_statistics(user)

@router.get("/analytics")
async def get_report_analytics(user: dict = Depends(get_current_user)):
    """Get report analytics summary (admin/directiva/tesorero only)"""
    return await statistics_service.get_report_analytics(user)

@router.get("/chat")
async def get_chat_statistics(user: dict = Depends(get_current_user)):
    """Get chat statistics (admin/directiva/tesorero only)"""
    return await statistics_service.get_chat_statistics(user)