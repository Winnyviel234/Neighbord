from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from app.core.security import get_current_user
from app.modules.payments.service import PaymentService
from app.modules.payments.model import PaymentCreate, PaymentVerify, StrikePaymentCreate, StrikePaymentResponse

router = APIRouter(prefix="/payments", tags=["payments"])

payment_service = PaymentService()

router = APIRouter(prefix="/payments", tags=["payments"])

payment_service = PaymentService()

@router.get("", response_model=list)
async def get_payments(
    estado: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    """Get payments for current user"""
    return await payment_service.get_user_payments(user["id"], user)

@router.get("/all")
async def get_all_payments(
    estado: Optional[str] = Query(None),
    user: dict = Depends(get_current_user)
):
    """Get all payments (admin/directiva/tesorero only)"""
    return await payment_service.get_all_payments(user, estado)

@router.post("")
async def create_payment(
    payload: PaymentCreate,
    user: dict = Depends(get_current_user)
):
    """Create payment"""
    return await payment_service.create_payment(payload, user)

@router.patch("/{payment_id}/verify")
async def verify_payment(
    payment_id: UUID,
    payload: PaymentVerify,
    user: dict = Depends(get_current_user)
):
    """Verify payment (admin/tesorero only)"""
    return await payment_service.verify_payment(payment_id, payload, user)

@router.get("/fees")
async def get_fees():
    """Get active fees"""
    return await payment_service.get_fees()

@router.get("/fees/{fee_id}/status")
async def get_fee_status(
    fee_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Check if user paid a fee"""
    return await payment_service.get_user_fee_status(user["id"], fee_id)

# Strike Payment Endpoints
@router.post("/strike", response_model=StrikePaymentResponse)
async def create_strike_payment(
    payload: StrikePaymentCreate,
    user: dict = Depends(get_current_user)
):
    """Create payment with Strike (Lightning Network)"""
    return await payment_service.create_strike_payment(payload, user)

@router.get("/{payment_id}/strike-status")
async def check_strike_payment_status(
    payment_id: UUID,
    user: dict = Depends(get_current_user)
):
    """Check Strike payment status"""
    return await payment_service.check_strike_payment_status(payment_id, user)