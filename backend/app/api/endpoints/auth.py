from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.modules.auth.service import AuthService
from app.modules.auth.model import RegisterRequest, LoginRequest, PasswordChangeRequest, ProfileUpdateRequest, PasswordResetRequest, PasswordResetConfirmRequest
from app.schemas.schemas import LoginIn, PasswordChangeIn, ProfileUpdateIn, RegisterIn

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()


@router.post("/register")
async def register(payload: RegisterIn):
    data = RegisterRequest(**payload.model_dump())
    return await auth_service.register(data)


@router.post("/login")
async def login(payload: LoginIn):
    data = LoginRequest(**payload.model_dump())
    return await auth_service.login(data)


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return await auth_service.get_current_user(user["id"])


@router.patch("/me")
async def update_me(payload: ProfileUpdateIn, user: dict = Depends(get_current_user)):
    data = ProfileUpdateRequest(**payload.model_dump())
    return await auth_service.update_profile(user["id"], data)


@router.post("/change-password")
async def change_password(payload: PasswordChangeIn, user: dict = Depends(get_current_user)):
    data = PasswordChangeRequest(**payload.model_dump())
    return await auth_service.change_password(user["id"], data)


@router.post("/password-reset/request")
async def request_password_reset(payload: PasswordResetRequest):
    return await auth_service.request_password_reset(payload)


@router.post("/password-reset/confirm")
async def confirm_password_reset(payload: PasswordResetConfirmRequest):
    return await auth_service.reset_password(payload)
