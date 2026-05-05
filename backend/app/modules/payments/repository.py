from typing import List, Optional, Dict, Any
from uuid import UUID
from app.core.supabase import table

class PaymentRepository:
    def __init__(self):
        self.payments_table = table("pagos")
        self.fees_table = table("cuotas")
        self.payments_fees_table = table("pagos_cuotas")
    
    async def get_user_payments(self, user_id: UUID, estado: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get payments for a user"""
        query = self.payments_table.select("""
            pagos.*,
            usuarios.nombre as vecino_nombre
        """).eq("vecino_id", str(user_id))
        
        if estado:
            query = query.eq("estado", estado)
        
        result = query.execute()
        return result.data or []
    
    async def get_all_payments(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get all payments with optional filters"""
        query = self.payments_table.select("""
            pagos.*,
            usuarios.nombre as vecino_nombre,
            verificador.nombre as verificador_nombre
        """)
        
        if filters:
            if filters.get("estado"):
                query = query.eq("estado", filters["estado"])
            if filters.get("user_id"):
                query = query.eq("vecino_id", str(filters["user_id"]))
        
        result = query.execute()
        return result.data or []
    
    async def create_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new payment"""
        result = self.payments_table.insert(data).execute()
        return result.data[0]
    
    async def update_payment(self, payment_id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update payment"""
        result = self.payments_table.update(data).eq("id", str(payment_id)).execute()
        return result.data[0] if result.data else None
    
    async def get_fees(self, estado: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get fees"""
        query = self.fees_table.select("*")
        if estado:
            query = query.eq("estado", estado)
        result = query.execute()
        return result.data or []
    
    async def get_user_fee_status(self, user_id: UUID, fee_id: UUID) -> Optional[Dict[str, Any]]:
        """Check if user paid a fee"""
        result = self.payments_fees_table.select("*").eq("vecino_id", str(user_id)).eq("cuota_id", str(fee_id)).single().execute()
        return result.data
    
    async def create_fee_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fee payment"""
        result = self.payments_fees_table.insert(data).execute()
        return result.data[0]