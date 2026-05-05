"""
Banking integration models for external financial systems
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


class BankAccount(BaseModel):
    """Bank account information"""
    id: str
    user_id: str
    bank_name: str
    account_number: str  # Masked for security
    account_type: str  # checking, savings, etc.
    currency: str = "USD"
    is_active: bool = True
    linked_at: datetime
    last_sync: Optional[datetime]
    balance: Optional[Decimal]


class BankTransaction(BaseModel):
    """Bank transaction record"""
    id: str
    account_id: str
    transaction_id: str  # Bank's transaction ID
    amount: Decimal
    currency: str = "USD"
    description: str
    transaction_date: datetime
    transaction_type: str  # debit, credit
    category: Optional[str]
    merchant: Optional[str]
    reference: Optional[str]
    imported_at: datetime
    raw_data: Dict[str, Any]


class BankIntegration(BaseModel):
    """Bank integration configuration"""
    id: str
    name: str  # plaid, stripe, banco_xyz, etc.
    display_name: str
    api_base_url: str
    client_id: str
    client_secret: str
    enabled: bool = True
    supported_countries: List[str] = ["US"]
    features: List[str] = []  # account_sync, payment_initiation, etc.


class BankConnection(BaseModel):
    """User's connection to a bank"""
    id: str
    user_id: str
    integration_id: str
    external_id: str  # Bank's connection ID
    status: str  # connected, disconnected, error
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_expires_at: Optional[datetime]
    connected_at: datetime
    last_sync: Optional[datetime]
    error_message: Optional[str]


class BankSyncResult(BaseModel):
    """Result of bank account synchronization"""
    accounts_synced: int
    transactions_synced: int
    new_transactions: int
    errors: List[str]
    sync_time: datetime


class PaymentInitiation(BaseModel):
    """Payment initiation request"""
    id: str
    user_id: str
    amount: Decimal
    currency: str = "USD"
    description: str
    recipient_account: str
    recipient_name: str
    reference: Optional[str]
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime
    processed_at: Optional[datetime]
    external_transaction_id: Optional[str]


class BankWebhookEvent(BaseModel):
    """Bank webhook event"""
    event_type: str
    integration_id: str
    connection_id: str
    data: Dict[str, Any]
    received_at: datetime