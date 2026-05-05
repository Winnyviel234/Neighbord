"""
Banking integration API routes
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel

from app.core.security import get_current_user, require_role
from app.modules.banking.models import BankAccount, PaymentInitiation, BankSyncResult
from app.modules.banking.service import banking_service


router = APIRouter(prefix="/banking", tags=["banking"])


class CreateBankConnectionRequest(BaseModel):
    integration_id: str
    public_token: str


class InitiatePaymentRequest(BaseModel):
    amount: float
    currency: str = "USD"
    description: str
    recipient_account: str
    recipient_name: str
    reference: Optional[str] = None


@router.get("/integrations")
async def get_banking_integrations():
    """Get available banking integrations"""
    integrations = []
    for integration in banking_service.integrations.values():
        if integration.enabled:
            integrations.append({
                "id": integration.id,
                "name": integration.name,
                "display_name": integration.display_name,
                "supported_countries": integration.supported_countries,
                "features": integration.features
            })

    return {"integrations": integrations}


@router.post("/connections")
async def create_bank_connection(
    request: CreateBankConnectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a bank connection"""
    try:
        connection = await banking_service.create_bank_connection(
            user_id=current_user["id"],
            integration_id=request.integration_id,
            public_token=request.public_token
        )

        return {
            "connection_id": connection.id,
            "status": connection.status,
            "connected_at": connection.connected_at
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bank connection: {str(e)}")


@router.get("/connections")
async def get_bank_connections(
    current_user: dict = Depends(get_current_user)
):
    """Get user's bank connections"""
    try:
        result = banking_service.supabase.table("bank_connections").select("""
            id, integration_id, status, connected_at, last_sync, error_message,
            integrations(name, display_name)
        """).eq("user_id", current_user["id"]).execute()

        connections = []
        for item in result.data:
            connections.append({
                "id": item["id"],
                "integration": {
                    "id": item["integration_id"],
                    "name": item["integrations"]["name"],
                    "display_name": item["integrations"]["display_name"]
                },
                "status": item["status"],
                "connected_at": item["connected_at"],
                "last_sync": item["last_sync"],
                "error_message": item["error_message"]
            })

        return {"connections": connections}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connections: {str(e)}")


@router.post("/connections/{connection_id}/sync")
async def sync_bank_connection(
    connection_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Sync bank accounts for a connection"""
    try:
        # Verify ownership
        connection_result = banking_service.supabase.table("bank_connections").select("user_id").eq("id", connection_id).execute()
        if not connection_result.data or connection_result.data[0]["user_id"] != current_user["id"]:
            raise HTTPException(status_code=404, detail="Bank connection not found")

        # Run sync in background
        background_tasks.add_task(banking_service.sync_bank_accounts, connection_id)

        return {"message": "Bank sync started in background"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start sync: {str(e)}")


@router.get("/accounts")
async def get_bank_accounts(
    current_user: dict = Depends(get_current_user)
):
    """Get user's bank accounts"""
    try:
        accounts = await banking_service.get_user_bank_accounts(current_user["id"])
        return {"accounts": accounts}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get accounts: {str(e)}")


@router.post("/payments")
async def initiate_payment(
    request: InitiatePaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Initiate a bank payment"""
    try:
        payment = await banking_service.initiate_payment(
            user_id=current_user["id"],
            payment_data=request.dict()
        )

        return {
            "payment_id": payment.id,
            "status": payment.status,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "created_at": payment.created_at
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate payment: {str(e)}")


@router.get("/payments")
async def get_payment_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get user's payment history"""
    try:
        payments = await banking_service.get_user_payments(current_user["id"], limit=limit)
        return {"payments": payments}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payments: {str(e)}")


@router.post("/webhooks/{integration_id}")
async def handle_bank_webhook(
    integration_id: str,
    webhook_data: dict,
    background_tasks: BackgroundTasks
):
    """Handle webhooks from banking providers"""
    try:
        # Process webhook in background
        background_tasks.add_task(banking_service.handle_bank_webhook, integration_id, webhook_data)

        return {"status": "webhook_received"}

    except Exception as e:
        # Don't expose internal errors to webhook providers
        raise HTTPException(status_code=200, detail="Webhook processed")


# Admin endpoints
@router.get("/admin/connections")
async def get_all_bank_connections(
    current_user: dict = Depends(require_role("admin"))
):
    """Get all bank connections (Admin only)"""
    try:
        result = banking_service.supabase.table("bank_connections").select("""
            id, user_id, integration_id, status, connected_at, last_sync,
            users(name, email)
        """).execute()

        connections = []
        for item in result.data:
            connections.append({
                "id": item["id"],
                "user": {
                    "id": item["user_id"],
                    "name": item["users"]["name"],
                    "email": item["users"]["email"]
                },
                "integration_id": item["integration_id"],
                "status": item["status"],
                "connected_at": item["connected_at"],
                "last_sync": item["last_sync"]
            })

        return {"connections": connections}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connections: {str(e)}")


@router.get("/admin/payments")
async def get_all_payments(
    limit: int = 100,
    current_user: dict = Depends(require_role("admin"))
):
    """Get all payment initiations (Admin only)"""
    try:
        result = banking_service.supabase.table("payment_initiations").select("""
            id, user_id, amount, currency, description, status, created_at, processed_at,
            users(name, email)
        """).order("created_at", desc=True).limit(limit).execute()

        payments = []
        for item in result.data:
            payments.append({
                "id": item["id"],
                "user": {
                    "id": item["user_id"],
                    "name": item["users"]["name"],
                    "email": item["users"]["email"]
                },
                "amount": item["amount"],
                "currency": item["currency"],
                "description": item["description"],
                "status": item["status"],
                "created_at": item["created_at"],
                "processed_at": item["processed_at"]
            })

        return {"payments": payments}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payments: {str(e)}")