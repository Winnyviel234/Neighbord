"""
Webhook repository for database operations
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.core.supabase import table
from app.modules.webhooks.model import WebhookSubscription, WebhookDelivery, WebhookEvent


class WebhookRepository:
    """Repository for webhook operations"""

    def __init__(self):
        pass

    async def create_subscription(self, subscription: WebhookSubscription) -> WebhookSubscription:
        """Create a new webhook subscription"""
        data = {
            "id": subscription.id,
            "url": subscription.url,
            "events": json.dumps(subscription.events),
            "secret": subscription.secret,
            "active": subscription.active,
            "created_at": subscription.created_at.isoformat(),
            "updated_at": subscription.updated_at.isoformat(),
            "delivery_attempts": subscription.delivery_attempts,
            "max_retries": subscription.max_retries
        }

        result = table("webhook_subscriptions").insert(data).execute()
        return WebhookSubscription(**result.data[0])

    async def get_subscription(self, subscription_id: str) -> Optional[WebhookSubscription]:
        """Get webhook subscription by ID"""
        result = table("webhook_subscriptions").select("*").eq("id", subscription_id).execute()

        if not result.data:
            return None

        data = result.data[0]
        data["events"] = json.loads(data["events"])
        return WebhookSubscription(**data)

    async def get_active_subscriptions(self, event_type: str) -> List[WebhookSubscription]:
        """Get all active subscriptions for an event type"""
        result = table("webhook_subscriptions") \
            .select("*") \
            .eq("active", True) \
            .execute()

        subscriptions = []
        for item in result.data:
            item["events"] = json.loads(item["events"])
            sub = WebhookSubscription(**item)
            if event_type in sub.events:
                subscriptions.append(sub)

        return subscriptions

    async def update_subscription(self, subscription_id: str, updates: Dict[str, Any]) -> Optional[WebhookSubscription]:
        """Update webhook subscription"""
        updates["updated_at"] = datetime.utcnow().isoformat()

        result = table("webhook_subscriptions") \
            .update(updates) \
            .eq("id", subscription_id) \
            .execute()

        if not result.data:
            return None

        data = result.data[0]
        data["events"] = json.loads(data["events"])
        return WebhookSubscription(**data)

    async def delete_subscription(self, subscription_id: str) -> bool:
        """Delete webhook subscription"""
        result = table("webhook_subscriptions") \
            .delete() \
            .eq("id", subscription_id) \
            .execute()

        return len(result.data) > 0

    async def list_subscriptions(self, skip: int = 0, limit: int = 50) -> List[WebhookSubscription]:
        """List all webhook subscriptions"""
        result = table("webhook_subscriptions") \
            .select("*") \
            .range(skip, skip + limit - 1) \
            .execute()

        subscriptions = []
        for item in result.data:
            item["events"] = json.loads(item["events"])
            subscriptions.append(WebhookSubscription(**item))

        return subscriptions

    async def log_delivery_attempt(self, delivery: WebhookDelivery) -> WebhookDelivery:
        """Log a webhook delivery attempt"""
        data = {
            "id": delivery.id,
            "subscription_id": delivery.subscription_id,
            "event_id": delivery.event_id,
            "url": delivery.url,
            "payload": json.dumps(delivery.payload),
            "status_code": delivery.status_code,
            "response_body": delivery.response_body,
            "success": delivery.success,
            "error_message": delivery.error_message,
            "attempt_number": delivery.attempt_number,
            "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None
        }

        result = table("webhook_deliveries").insert(data).execute()
        return WebhookDelivery(**result.data[0])

    async def get_delivery_history(self, subscription_id: str, limit: int = 20) -> List[WebhookDelivery]:
        """Get delivery history for a subscription"""
        result = table("webhook_deliveries") \
            .select("*") \
            .eq("subscription_id", subscription_id) \
            .order("delivered_at", desc=True) \
            .limit(limit) \
            .execute()

        deliveries = []
        for item in result.data:
            item["payload"] = json.loads(item["payload"])
            deliveries.append(WebhookDelivery(**item))

        return deliveries

    async def log_event(self, event: WebhookEvent) -> WebhookEvent:
        """Log a webhook event"""
        data = {
            "id": event.id,
            "event_type": event.event_type,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "data": json.dumps(event.data),
            "timestamp": event.timestamp.isoformat(),
            "source": event.source
        }

        result = table("webhook_events").insert(data).execute()
        return WebhookEvent(**result.data[0])

    async def get_failed_deliveries(self, hours_back: int = 24) -> List[WebhookDelivery]:
        """Get failed deliveries from the last N hours for retry"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)

        result = table("webhook_deliveries") \
            .select("*") \
            .eq("success", False) \
            .gte("delivered_at", cutoff_time.isoformat()) \
            .execute()

        deliveries = []
        for item in result.data:
            item["payload"] = json.loads(item["payload"])
            deliveries.append(WebhookDelivery(**item))

        return deliveries