from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.modules.auth.service import AuthService
from app.modules.auth.model import RegisterRequest, LoginRequest, PasswordChangeRequest, PasswordResetConfirmRequest, PasswordResetRequest, ProfileUpdateRequest

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()

@router.post("/register")
async def register(payload: RegisterRequest):
    """Register new user"""
    return await auth_service.register(payload)

@router.post("/login")
async def login(payload: LoginRequest):
    """Authenticate user"""
    return await auth_service.login(payload)

@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return await auth_service.get_current_user(user["id"])

@router.patch("/me")
async def update_me(payload: ProfileUpdateRequest, user: dict = Depends(get_current_user)):
    """Update current user profile"""
    return await auth_service.update_profile(user["id"], payload)

@router.post("/change-password")
async def change_password(payload: PasswordChangeRequest, user: dict = Depends(get_current_user)):
    """Change current user password"""
    return await auth_service.change_password(user["id"], payload)

@router.post("/password-reset/request")
async def request_password_reset(payload: PasswordResetRequest):
    """Request a secure password reset link"""
    return await auth_service.request_password_reset(payload)

@router.post("/password-reset/confirm")
async def confirm_password_reset(payload: PasswordResetConfirmRequest):
    """Confirm password reset with a one-time token"""
    return await auth_service.reset_password(payload)
