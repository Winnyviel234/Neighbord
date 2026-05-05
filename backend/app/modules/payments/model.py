from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime, date

class Payment(BaseModel):
    id: Optional[UUID]
    vecino_id: UUID
    concepto: str
    monto: float
    fecha_pago: date
    metodo: str = "efectivo"
    referencia: Optional[str] = None
    estado: str = "pendiente"
    comprobante_url: Optional[str] = None
    verificado_por: Optional[UUID] = None
    verificado_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    # Strike integration fields
    strike_invoice_id: Optional[str] = None
    strike_payment_request: Optional[str] = None
    strike_lnurl: Optional[str] = None
    strike_expires_at: Optional[datetime] = None

class PaymentCreate(BaseModel):
    concepto: str
    monto: float
    fecha_pago: date
    metodo: str = "efectivo"
    referencia: Optional[str] = None
    use_strike: bool = False  # New field to indicate Strike payment

class PaymentVerify(BaseModel):
    estado: str  # verified or rejected
    comprobante_url: Optional[str] = None

class StrikePaymentCreate(BaseModel):
    concepto: str
    monto: float
    fecha_pago: date

class StrikePaymentResponse(BaseModel):
    invoice_id: str
    payment_request: str
    lnurl: str
    amount: str
    currency: str
    description: str
    state: str
    created_at: str
    expires_at: str
    payment_id: UUID  # Reference to our payment record

class PaymentCreate(BaseModel):
    concepto: str
    monto: float
    fecha_pago: date
    metodo: str = "efectivo"
    referencia: Optional[str] = None

class PaymentVerify(BaseModel):
    estado: str  # verified or rejected
    comprobante_url: Optional[str] = None

class Fee(BaseModel):
    id: Optional[UUID]
    titulo: str
    descripcion: Optional[str] = None
    monto: float
    fecha_vencimiento: date
    estado: str = "activa"
    creado_por: UUID
    created_at: Optional[datetime] = None

class FeeCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    monto: float
    fecha_vencimiento: date

class PaymentResponse(BaseModel):
    id: UUID
    vecino_id: UUID
    vecino_nombre: str
    concepto: str
    monto: float
    fecha_pago: date
    metodo: str
    referencia: Optional[str]
    estado: str
    comprobante_url: Optional[str]
    verificado_por: Optional[str] = None
    verificado_at: Optional[datetime] = None
    created_at: datetime