"""
Webhook service for managing webhook subscriptions and deliveries
"""

import asyncio
import hashlib
import hmac
import json
import secrets
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import aiohttp

from app.core.cache.redis_cache import cache_manager
from app.modules.webhooks.model import WebhookSubscription, WebhookDelivery, WebhookEvent, WebhookPayload
from app.modules.webhooks.repository import WebhookRepository


class WebhookService:
    """Service for webhook operations"""

    def __init__(self):
        self.repo = WebhookRepository()
        self._http_client = None

    @property
    def http_client(self):
        """Lazy initialization of HTTP client"""
        if self._http_client is None or self._http_client.closed:
            self._http_client = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)  # 30 second timeout
            )
        return self._http_client

    async def close(self):
        """Close HTTP client"""
        if self._http_client and not self._http_client.closed:
            await self._http_client.close()

    def generate_secret(self) -> str:
        """Generate a secure webhook secret"""
        return secrets.token_urlsafe(32)

    def generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        expected_signature = self.generate_signature(payload, secret)
        return hmac.compare_digest(expected_signature, signature)

    async def create_subscription(self, url: str, events: List[str], secret: Optional[str] = None) -> WebhookSubscription:
        """Create a new webhook subscription"""
        if not secret:
            secret = self.generate_secret()

        subscription = WebhookSubscription(
            id=str(uuid.uuid4()),
            url=url,
            events=events,
            secret=secret
        )

        return await self.repo.create_subscription(subscription)

    async def trigger_event(self, event_type: str, resource_type: str, resource_id: str, data: Dict[str, Any]) -> None:
        """Trigger a webhook event to all subscribed endpoints"""
        # Log the event
        event = WebhookEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            data=data
        )

        await self.repo.log_event(event)

        # Get active subscriptions for this event type
        subscriptions = await self.repo.get_active_subscriptions(event_type)

        if not subscriptions:
            return

        # Create payload
        payload = WebhookPayload(
            event_id=event.id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            timestamp=event.timestamp,
            data=data
        )

        # Send to all subscriptions asynchronously
        tasks = []
        for subscription in subscriptions:
            tasks.append(self._deliver_webhook(subscription, payload))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _deliver_webhook(self, subscription: WebhookSubscription, payload: WebhookPayload) -> None:
        """Deliver webhook to a single subscription"""
        try:
            # Prepare payload
            payload_dict = payload.dict()
            payload_json = json.dumps(payload_dict, default=str)

            # Generate signature
            signature = self.generate_signature(payload_json, subscription.secret)
            payload_dict["signature"] = signature

            # Create delivery record
            delivery = WebhookDelivery(
                id=str(uuid.uuid4()),
                subscription_id=subscription.id,
                event_id=payload.event_id,
                url=subscription.url,
                payload=payload_dict,
                attempt_number=1
            )

            # Send webhook
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Neighbord-Webhook/1.0",
                "X-Webhook-Signature": signature,
                "X-Webhook-ID": delivery.id,
                "X-Event-Type": payload.event_type
            }

            async with self.http_client.post(
                subscription.url,
                json=payload_dict,
                headers=headers
            ) as response:
                delivery.status_code = response.status
                delivery.response_body = await response.text()
                delivery.success = response.status == 200
                delivery.delivered_at = datetime.utcnow()

                if not delivery.success:
                    delivery.error_message = f"HTTP {response.status}: {delivery.response_body}"

            # Log delivery attempt
            await self.repo.log_delivery_attempt(delivery)

            # Update subscription stats
            if delivery.success:
                await self.repo.update_subscription(subscription.id, {
                    "last_delivery": delivery.delivered_at.isoformat(),
                    "delivery_attempts": 0  # Reset on success
                })
            else:
                # Increment retry count
                await self.repo.update_subscription(subscription.id, {
                    "delivery_attempts": subscription.delivery_attempts + 1
                })

                # Deactivate if max retries exceeded
                if subscription.delivery_attempts + 1 >= subscription.max_retries:
                    await self.repo.update_subscription(subscription.id, {"active": False})

        except Exception as e:
            # Log failed delivery
            delivery = WebhookDelivery(
                id=str(uuid.uuid4()),
                subscription_id=subscription.id,
                event_id=payload.event_id,
                url=subscription.url,
                payload=payload_dict,
                success=False,
                error_message=str(e),
                attempt_number=1
            )
            await self.repo.log_delivery_attempt(delivery)

    async def retry_failed_deliveries(self) -> int:
        """Retry failed webhook deliveries"""
        failed_deliveries = await self.repo.get_failed_deliveries(hours_back=24)
        retry_count = 0

        for delivery in failed_deliveries:
            subscription = await self.repo.get_subscription(delivery.subscription_id)
            if not subscription or not subscription.active:
                continue

            # Create new payload from delivery
            payload = WebhookPayload(**delivery.payload)

            # Retry delivery
            await self._deliver_webhook(subscription, payload)
            retry_count += 1

        return retry_count

    async def get_subscription_stats(self, subscription_id: str) -> Dict[str, Any]:
        """Get statistics for a webhook subscription"""
        subscription = await self.repo.get_subscription(subscription_id)
        if not subscription:
            return None

        deliveries = await self.repo.get_delivery_history(subscription_id, limit=100)

        total_deliveries = len(deliveries)
        successful_deliveries = len([d for d in deliveries if d.success])
        failed_deliveries = total_deliveries - successful_deliveries

        success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0

        return {
            "subscription_id": subscription_id,
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "success_rate": round(success_rate, 2),
            "last_delivery": subscription.last_delivery,
            "active": subscription.active
        }


# Global webhook service instance
webhook_service = WebhookService()