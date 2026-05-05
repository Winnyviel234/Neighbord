from typing import List, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from datetime import datetime, timezone
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.model import PaymentCreate, PaymentVerify, PaymentResponse, StrikePaymentCreate, StrikePaymentResponse
from app.services.strike_service import StrikePaymentService

class PaymentService:
    def __init__(self):
        self.repo = PaymentRepository()
        self.strike_service = StrikePaymentService()
    
    async def get_user_payments(self, user_id: UUID, current_user: Dict[str, Any]) -> List[PaymentResponse]:
        """Get payments for a user"""
        # Users can see their own payments, admin/directiva/tesorero can see all
        if str(user_id) != current_user["id"] and current_user.get("role_name") not in ["admin", "directiva", "tesorero"]:
            raise HTTPException(403, "No tienes permisos para ver estos pagos")
        
        payments = await self.repo.get_user_payments(user_id)
        return [PaymentResponse(**p) for p in payments]
    
    async def get_all_payments(self, current_user: Dict[str, Any], estado: str = None) -> List[PaymentResponse]:
        """Get all payments (admin/directiva/tesorero only)"""
        if current_user.get("role_name") not in ["admin", "directiva", "tesorero"]:
            raise HTTPException(403, "No tienes permisos para ver todos los pagos")
        
        filters = {}
        if estado:
            filters["estado"] = estado
        
        payments = await self.repo.get_all_payments(filters)
        return [PaymentResponse(**p) for p in payments]
    
    async def create_payment(self, data: PaymentCreate, current_user: Dict[str, Any]) -> PaymentResponse:
        """Create payment"""
        payment_data = {
            "vecino_id": current_user["id"],
            "concepto": data.concepto,
            "monto": data.monto,
            "fecha_pago": data.fecha_pago,
            "metodo": data.metodo,
            "referencia": data.referencia,
            "estado": "pendiente"
        }
        
        payment = await self.repo.create_payment(payment_data)
        return PaymentResponse(**payment)
    
    async def verify_payment(self, payment_id: UUID, data: PaymentVerify, current_user: Dict[str, Any]) -> PaymentResponse:
        """Verify payment (admin/tesorero only)"""
        if current_user.get("role_name") not in ["admin", "tesorero"]:
            raise HTTPException(403, "No tienes permisos para verificar pagos")
        
        update_data = {
            "estado": data.estado,
            "comprobante_url": data.comprobante_url,
            "verificado_por": current_user["id"],
            "verificado_at": datetime.now(timezone.utc)
        }
        
        payment = await self.repo.update_payment(payment_id, update_data)
        if not payment:
            raise HTTPException(404, "Pago no encontrado")
        
        return PaymentResponse(**payment)
    
    async def get_fees(self) -> List[Dict[str, Any]]:
        """Get active fees"""
        fees = await self.repo.get_fees(estado="activa")
        return fees
    
    async def get_user_fee_status(self, user_id: UUID, fee_id: UUID) -> Dict[str, Any]:
        """Check if user paid a fee"""
        status = await self.repo.get_user_fee_status(user_id, fee_id)
        return {
            "paid": status is not None,
            "payment_date": status.get("fecha_pago") if status else None,
            "status": status.get("estado") if status else "pending"
        }

    async def create_strike_payment(self, data: StrikePaymentCreate, current_user: Dict[str, Any]) -> StrikePaymentResponse:
        """Create payment with Strike integration"""
        try:
            # Create Strike invoice
            strike_data = await self.strike_service.create_payment_link(
                amount=data.monto,
                description=data.concepto
            )

            # Create payment record in our database
            payment_data = {
                "vecino_id": current_user["id"],
                "concepto": data.concepto,
                "monto": data.monto,
                "fecha_pago": data.fecha_pago,
                "metodo": "strike",
                "estado": "pending",
                "strike_invoice_id": strike_data["invoice_id"],
                "strike_payment_request": strike_data["payment_request"],
                "strike_lnurl": strike_data["lnurl"],
                "strike_expires_at": strike_data["expires_at"]
            }

            payment = await self.repo.create_payment(payment_data)

            # Return Strike payment response
            return StrikePaymentResponse(
                invoice_id=strike_data["invoice_id"],
                payment_request=strike_data["payment_request"],
                lnurl=strike_data["lnurl"],
                amount=strike_data["amount"],
                currency=strike_data["currency"],
                description=strike_data["description"],
                state=strike_data["state"],
                created_at=strike_data["created_at"],
                expires_at=strike_data["expires_at"],
                payment_id=payment["id"]
            )

        except Exception as e:
            raise HTTPException(500, f"Error creating Strike payment: {str(e)}")

    async def check_strike_payment_status(self, payment_id: UUID, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Check Strike payment status and update if paid"""
        # Get payment from database
        payment = await self.repo.get_payment_by_id(payment_id)
        if not payment:
            raise HTTPException(404, "Pago no encontrado")

        # Check ownership or admin permissions
        if str(payment["vecino_id"]) != current_user["id"] and current_user.get("role_name") not in ["admin", "directiva", "tesorero"]:
            raise HTTPException(403, "No tienes permisos para ver este pago")

        if not payment.get("strike_invoice_id"):
            raise HTTPException(400, "Este pago no es de Strike")

        try:
            # Check status with Strike
            strike_status = await self.strike_service.check_payment_status(payment["strike_invoice_id"])

            # Update payment status if paid
            if strike_status == "paid" and payment["estado"] != "verified":
                await self.repo.update_payment(payment_id, {
                    "estado": "verified",
                    "verificado_at": datetime.now(timezone.utc)
                })
                payment["estado"] = "verified"

            return {
                "payment_id": payment_id,
                "strike_status": strike_status,
                "payment_status": payment["estado"],
                "invoice_id": payment["strike_invoice_id"],
                "updated": strike_status == "paid" and payment["estado"] == "verified"
            }

        except Exception as e:
            raise HTTPException(500, f"Error checking Strike payment status: {str(e)}")