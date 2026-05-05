"""
Banking integration service for external financial systems
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal
import aiohttp

from app.core.supabase import table
from app.modules.banking.models import (
    BankAccount, BankTransaction, BankIntegration,
    BankConnection, BankSyncResult, PaymentInitiation, BankWebhookEvent
)


class BankingService:
    """Service for banking integrations"""

    def __init__(self):
        # Supported banking integrations
        self.integrations = {
            "plaid": BankIntegration(
                id="plaid",
                name="plaid",
                display_name="Plaid",
                api_base_url="https://sandbox.plaid.com",  # Use sandbox for development
                client_id="",  # Set via environment
                client_secret="",  # Set via environment
                enabled=True,
                supported_countries=["US"],
                features=["account_sync", "transaction_sync"]
            ),
            "stripe": BankIntegration(
                id="stripe",
                name="stripe",
                display_name="Stripe",
                api_base_url="https://api.stripe.com/v1",
                client_id="",  # Set via environment
                client_secret="",  # Set via environment
                enabled=True,
                supported_countries=["US", "CA", "GB"],
                features=["payment_initiation", "account_sync"]
            ),
            # Add more integrations as needed
        }

    def get_integration(self, integration_id: str) -> Optional[BankIntegration]:
        """Get banking integration configuration"""
        return self.integrations.get(integration_id)

    async def create_bank_connection(self, user_id: str, integration_id: str, public_token: str) -> BankConnection:
        """Create a bank connection using public token"""
        integration = self.get_integration(integration_id)
        if not integration:
            raise ValueError(f"Integration '{integration_id}' not supported")

        # Exchange public token for access token (implementation depends on provider)
        access_token = await self._exchange_public_token(integration, public_token)

        connection = BankConnection(
            id=str(uuid.uuid4()),
            user_id=user_id,
            integration_id=integration_id,
            external_id="",  # Set by the provider
            status="connected",
            access_token=access_token,
            connected_at=datetime.utcnow()
        )

        # Save connection
        data = {
            "id": connection.id,
            "user_id": connection.user_id,
            "integration_id": connection.integration_id,
            "external_id": connection.external_id,
            "status": connection.status,
            "access_token": connection.access_token,
            "connected_at": connection.connected_at.isoformat()
        }

        result = table("bank_connections").insert(data).execute()
        return BankConnection(**result.data[0])

    async def _exchange_public_token(self, integration: BankIntegration, public_token: str) -> str:
        """Exchange public token for access token (provider-specific)"""
        if integration.name == "plaid":
            return await self._plaid_exchange_token(integration, public_token)
        elif integration.name == "stripe":
            return await self._stripe_exchange_token(integration, public_token)
        else:
            raise ValueError(f"Token exchange not implemented for {integration.name}")

    async def _plaid_exchange_token(self, integration: BankIntegration, public_token: str) -> str:
        """Exchange Plaid public token for access token"""
        async with aiohttp.ClientSession() as session:
            data = {
                "client_id": integration.client_id,
                "secret": integration.client_secret,
                "public_token": public_token
            }

            async with session.post(f"{integration.api_base_url}/item/public_token/exchange", json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"Plaid token exchange failed: {error_text}")

                result = await response.json()
                return result["access_token"]

    async def _stripe_exchange_token(self, integration: BankIntegration, public_token: str) -> str:
        """Exchange Stripe public token for access token"""
        # Stripe uses different flow - this is simplified
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {integration.client_secret}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            data = {
                "grant_type": "authorization_code",
                "code": public_token,
                "client_id": integration.client_id
            }

            async with session.post(f"{integration.api_base_url}/oauth/token", data=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"Stripe token exchange failed: {error_text}")

                result = await response.json()
                return result["access_token"]

    async def sync_bank_accounts(self, connection_id: str) -> BankSyncResult:
        """Sync bank accounts for a connection"""
        # Get connection
        connection_result = table("bank_connections").select("*").eq("id", connection_id).execute()
        if not connection_result.data:
            raise ValueError("Bank connection not found")

        connection = BankConnection(**connection_result.data[0])
        integration = self.get_integration(connection.integration_id)

        if not integration:
            raise ValueError("Integration not configured")

        # Sync accounts based on provider
        if integration.name == "plaid":
            return await self._sync_plaid_accounts(connection, integration)
        elif integration.name == "stripe":
            return await self._sync_stripe_accounts(connection, integration)
        else:
            raise ValueError(f"Account sync not implemented for {integration.name}")

    async def _sync_plaid_accounts(self, connection: BankConnection, integration: BankIntegration) -> BankSyncResult:
        """Sync accounts from Plaid"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json"
            }

            data = {
                "client_id": integration.client_id,
                "secret": integration.client_secret,
                "access_token": connection.access_token
            }

            async with session.post(f"{integration.api_base_url}/accounts/get", json=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"Plaid accounts sync failed: {error_text}")

                result = await response.json()
                accounts_data = result["accounts"]

                # Save accounts
                synced_accounts = 0
                for account_data in accounts_data:
                    account = BankAccount(
                        id=str(uuid.uuid4()),
                        user_id=connection.user_id,
                        bank_name=account_data.get("name", "Unknown Bank"),
                        account_number=f"****{account_data['mask']}" if account_data.get("mask") else "****0000",
                        account_type=account_data.get("type", "checking"),
                        currency=account_data.get("balances", {}).get("iso_currency_code", "USD"),
                        balance=Decimal(str(account_data.get("balances", {}).get("current", 0))),
                        linked_at=datetime.utcnow(),
                        last_sync=datetime.utcnow()
                    )

                    # Save account
                    account_dict = account.dict()
                    account_dict["balance"] = str(account.balance)
                    account_dict["linked_at"] = account.linked_at.isoformat()
                    account_dict["last_sync"] = account.last_sync.isoformat()

                    table("bank_accounts").insert(account_dict).execute()
                    synced_accounts += 1

                return BankSyncResult(
                    accounts_synced=synced_accounts,
                    transactions_synced=0,
                    new_transactions=0,
                    errors=[],
                    sync_time=datetime.utcnow()
                )

    async def _sync_stripe_accounts(self, connection: BankConnection, integration: BankIntegration) -> BankSyncResult:
        """Sync accounts from Stripe"""
        # Stripe account sync would be implemented here
        # This is a placeholder for the actual implementation
        return BankSyncResult(
            accounts_synced=0,
            transactions_synced=0,
            new_transactions=0,
            errors=["Stripe account sync not yet implemented"],
            sync_time=datetime.utcnow()
        )

    async def initiate_payment(self, user_id: str, payment_data: Dict[str, Any]) -> PaymentInitiation:
        """Initiate a payment through banking integration"""
        payment = PaymentInitiation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            amount=Decimal(str(payment_data["amount"])),
            currency=payment_data.get("currency", "USD"),
            description=payment_data["description"],
            recipient_account=payment_data["recipient_account"],
            recipient_name=payment_data["recipient_name"],
            reference=payment_data.get("reference"),
            created_at=datetime.utcnow()
        )

        # Save payment initiation
        payment_dict = payment.dict()
        payment_dict["amount"] = str(payment.amount)
        payment_dict["created_at"] = payment.created_at.isoformat()

        result = table("payment_initiations").insert(payment_dict).execute()

        # Here you would integrate with the actual banking provider
        # For now, we'll mark it as completed immediately
        await self._update_payment_status(payment.id, "completed")

        return PaymentInitiation(**result.data[0])

    async def _update_payment_status(self, payment_id: str, status: str, external_id: Optional[str] = None):
        """Update payment status"""
        update_data = {"status": status}
        if external_id:
            update_data["external_transaction_id"] = external_id
        if status in ["completed", "failed"]:
            update_data["processed_at"] = datetime.utcnow().isoformat()

        table("payment_initiations").update(update_data).eq("id", payment_id).execute()

    async def get_user_bank_accounts(self, user_id: str) -> List[BankAccount]:
        """Get user's bank accounts"""
        result = table("bank_accounts").select("*").eq("user_id", user_id).eq("is_active", True).execute()

        accounts = []
        for item in result.data:
            item["balance"] = Decimal(str(item["balance"])) if item.get("balance") else None
            accounts.append(BankAccount(**item))

        return accounts

    async def get_user_payments(self, user_id: str, limit: int = 50) -> List[PaymentInitiation]:
        """Get user's payment history"""
        result = table("payment_initiations").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()

        payments = []
        for item in result.data:
            item["amount"] = Decimal(str(item["amount"]))
            payments.append(PaymentInitiation(**item))

        return payments

    async def handle_bank_webhook(self, integration_id: str, webhook_data: Dict[str, Any]) -> BankWebhookEvent:
        """Handle webhook from banking provider"""
        event = BankWebhookEvent(
            event_type=webhook_data.get("webhook_type", "unknown"),
            integration_id=integration_id,
            connection_id=webhook_data.get("item_id", ""),
            data=webhook_data,
            received_at=datetime.utcnow()
        )

        # Save webhook event
        event_dict = event.dict()
        event_dict["received_at"] = event.received_at.isoformat()

        table("bank_webhook_events").insert(event_dict).execute()

        # Process webhook based on type
        if event.event_type == "TRANSACTIONS_UPDATE":
            # Trigger transaction sync
            await self.sync_bank_accounts(event.connection_id)

        return event


# Global banking service instance
banking_service = BankingService()