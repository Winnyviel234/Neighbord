from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.modules.auth.service import AuthService
from app.modules.auth.model import RegisterRequest, LoginRequest, PasswordChangeRequest, ProfileUpdateRequest
from app.schemas.schemas import LoginIn, PasswordChangeIn, ProfileUpdateIn, RegisterIn

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()


@router.post("/register")
def register(payload: RegisterIn):
    data = RegisterRequest(**payload.model_dump())
    return auth_service.register(data)


@router.post("/login")
def login(payload: LoginIn):
    data = LoginRequest(**payload.model_dump())
    return auth_service.login(data)


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return auth_service.get_current_user(user["id"])


@router.patch("/me")
def update_me(payload: ProfileUpdateIn, user: dict = Depends(get_current_user)):
    data = ProfileUpdateRequest(**payload.model_dump())
    return auth_service.update_profile(user["id"], data)


@router.post("/change-password")
def change_password(payload: PasswordChangeIn, user: dict = Depends(get_current_user)):
    data = PasswordChangeRequest(**payload.model_dump())
    return auth_service.change_password(user["id"], data)
