import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.config import settings

class StrikePaymentService:
    def __init__(self):
        self.api_key = settings.strike_api_key
        self.base_url = "https://api.strike.me/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def create_invoice(self, amount: float, currency: str = "USD", description: str = "") -> Dict[str, Any]:
        """
        Create a Strike invoice for payment
        """
        try:
            payload = {
                "amount": str(amount),
                "currency": currency,
                "description": description,
                "correlationId": f"neighbord-{datetime.now().timestamp()}"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/invoices",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 201:
                    return response.json()
                else:
                    raise Exception(f"Strike API error: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(f"Error creating Strike invoice: {str(e)}")

    async def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """
        Get invoice details from Strike
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/invoices/{invoice_id}",
                    headers=self.headers,
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Strike API error: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(f"Error getting Strike invoice: {str(e)}")

    async def check_payment_status(self, invoice_id: str) -> str:
        """
        Check if invoice has been paid
        Returns: 'pending', 'paid', 'expired', 'cancelled'
        """
        try:
            invoice = await self.get_invoice(invoice_id)
            state = invoice.get("state", "PENDING")

            # Map Strike states to our states
            state_mapping = {
                "PENDING": "pending",
                "PAID": "paid",
                "EXPIRED": "expired",
                "CANCELLED": "cancelled"
            }

            return state_mapping.get(state, "pending")

        except Exception as e:
            print(f"Error checking payment status: {str(e)}")
            return "pending"

    async def create_payment_link(self, amount: float, description: str = "Pago comunitario") -> Dict[str, Any]:
        """
        Create a payment invoice and return payment details
        """
        invoice = await self.create_invoice(amount, "USD", description)

        return {
            "invoice_id": invoice["invoiceId"],
            "payment_request": invoice["paymentRequest"],
            "lnurl": invoice.get("lnurl", ""),
            "amount": invoice["amount"]["amount"],
            "currency": invoice["amount"]["currency"],
            "description": invoice["description"],
            "state": invoice["state"],
            "created_at": invoice["created"],
            "expires_at": invoice["expiration"]
        }