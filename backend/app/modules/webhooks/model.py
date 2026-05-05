"""
Webhook models for external integrations
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class WebhookEvent(BaseModel):
    """Webhook event model"""
    id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Type of event (user.created, payment.completed, etc.)")
    resource_type: str = Field(..., description="Resource type (user, payment, complaint, etc.)")
    resource_id: str = Field(..., description="ID of the affected resource")
    data: Dict[str, Any] = Field(..., description="Event data payload")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    source: str = Field(..., description="Source system that triggered the event")


class WebhookSubscription(BaseModel):
    """Webhook subscription model"""
    id: str = Field(..., description="Unique subscription identifier")
    url: str = Field(..., description="Webhook endpoint URL")
    events: list[str] = Field(..., description="List of event types to subscribe to")
    secret: str = Field(..., description="Webhook secret for signature verification")
    active: bool = Field(default=True, description="Whether the subscription is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_delivery: Optional[datetime] = None
    delivery_attempts: int = Field(default=0, description="Number of delivery attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


class WebhookDelivery(BaseModel):
    """Webhook delivery attempt model"""
    id: str = Field(..., description="Unique delivery identifier")
    subscription_id: str = Field(..., description="Webhook subscription ID")
    event_id: str = Field(..., description="Event ID being delivered")
    url: str = Field(..., description="Delivery URL")
    payload: Dict[str, Any] = Field(..., description="Delivered payload")
    status_code: Optional[int] = Field(None, description="HTTP status code from delivery")
    response_body: Optional[str] = Field(None, description="Response body from webhook")
    success: bool = Field(default=False, description="Whether delivery was successful")
    error_message: Optional[str] = Field(None, description="Error message if delivery failed")
    attempt_number: int = Field(default=1, description="Attempt number")
    delivered_at: Optional[datetime] = Field(None, description="When delivery was successful")


class WebhookPayload(BaseModel):
    """Outgoing webhook payload"""
    event_id: str
    event_type: str
    resource_type: str
    resource_id: str
    timestamp: datetime
    source: str = "neighbord"
    data: Dict[str, Any]
    signature: Optional[str] = None  # HMAC signature for verification