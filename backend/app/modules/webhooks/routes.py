"""
Webhook API routes
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel

from app.core.security import get_current_user, require_roles
from app.modules.webhooks.model import WebhookSubscription
from app.modules.webhooks.service import webhook_service


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class CreateWebhookRequest(BaseModel):
    url: str
    events: List[str]
    secret: Optional[str] = None


class WebhookStats(BaseModel):
    subscription_id: str
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    success_rate: float
    last_delivery: Optional[str]
    active: bool


@router.post("/subscriptions", response_model=WebhookSubscription)
async def create_webhook_subscription(
    request: CreateWebhookRequest,
    current_user: dict = Depends(require_roles("admin"))
):
    """Create a new webhook subscription (Admin only)"""
    try:
        subscription = await webhook_service.create_subscription(
            url=request.url,
            events=request.events,
            secret=request.secret
        )
        return subscription
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create webhook subscription: {str(e)}")


@router.get("/subscriptions", response_model=List[WebhookSubscription])
async def list_webhook_subscriptions(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(require_roles("admin"))
):
    """List all webhook subscriptions (Admin only)"""
    try:
        subscriptions = await webhook_service.repo.list_subscriptions(skip=skip, limit=limit)
        return subscriptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list subscriptions: {str(e)}")


@router.get("/subscriptions/{subscription_id}", response_model=WebhookSubscription)
async def get_webhook_subscription(
    subscription_id: str,
    current_user: dict = Depends(require_roles("admin"))
):
    """Get webhook subscription by ID (Admin only)"""
    try:
        subscription = await webhook_service.repo.get_subscription(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Webhook subscription not found")
        return subscription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscription: {str(e)}")


@router.put("/subscriptions/{subscription_id}", response_model=WebhookSubscription)
async def update_webhook_subscription(
    subscription_id: str,
    updates: dict,
    current_user: dict = Depends(require_roles("admin"))
):
    """Update webhook subscription (Admin only)"""
    try:
        # Validate allowed fields
        allowed_fields = {"url", "events", "active", "max_retries"}
        filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

        subscription = await webhook_service.repo.update_subscription(subscription_id, filtered_updates)
        if not subscription:
            raise HTTPException(status_code=404, detail="Webhook subscription not found")
        return subscription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update subscription: {str(e)}")


@router.delete("/subscriptions/{subscription_id}")
async def delete_webhook_subscription(
    subscription_id: str,
    current_user: dict = Depends(require_roles("admin"))
):
    """Delete webhook subscription (Admin only)"""
    try:
        deleted = await webhook_service.repo.delete_subscription(subscription_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Webhook subscription not found")
        return {"message": "Webhook subscription deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete subscription: {str(e)}")


@router.get("/subscriptions/{subscription_id}/deliveries")
async def get_webhook_delivery_history(
    subscription_id: str,
    limit: int = 20,
    current_user: dict = Depends(require_roles("admin"))
):
    """Get delivery history for a webhook subscription (Admin only)"""
    try:
        deliveries = await webhook_service.repo.get_delivery_history(subscription_id, limit=limit)
        return {"deliveries": deliveries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get delivery history: {str(e)}")


@router.get("/subscriptions/{subscription_id}/stats", response_model=WebhookStats)
async def get_webhook_subscription_stats(
    subscription_id: str,
    current_user: dict = Depends(require_roles("admin"))
):
    """Get statistics for a webhook subscription (Admin only)"""
    try:
        stats = await webhook_service.get_subscription_stats(subscription_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Webhook subscription not found")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscription stats: {str(e)}")


@router.post("/retry-failed")
async def retry_failed_webhook_deliveries(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_roles("admin"))
):
    """Retry failed webhook deliveries (Admin only)"""
    try:
        # Run retry in background
        background_tasks.add_task(webhook_service.retry_failed_deliveries)
        return {"message": "Retry process started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start retry process: {str(e)}")


@router.post("/test/{subscription_id}")
async def test_webhook_subscription(
    subscription_id: str,
    current_user: dict = Depends(require_roles("admin"))
):
    """Send a test webhook to a subscription (Admin only)"""
    try:
        subscription = await webhook_service.repo.get_subscription(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Webhook subscription not found")

        # Send test event
        test_data = {
            "message": "This is a test webhook from Neighbord",
            "timestamp": str(datetime.utcnow()),
            "test": True
        }

        await webhook_service.trigger_event(
            event_type="test.ping",
            resource_type="webhook",
            resource_id=subscription_id,
            data=test_data
        )

        return {"message": "Test webhook sent successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send test webhook: {str(e)}")


# Available webhook events documentation
@router.get("/events")
async def get_available_webhook_events():
    """Get list of available webhook events"""
    events = {
        "user.created": "User account created",
        "user.updated": "User profile updated",
        "user.deleted": "User account deleted",
        "payment.completed": "Payment transaction completed",
        "payment.failed": "Payment transaction failed",
        "complaint.created": "New complaint/solicitud created",
        "complaint.updated": "Complaint status updated",
        "complaint.resolved": "Complaint marked as resolved",
        "meeting.created": "New meeting scheduled",
        "meeting.updated": "Meeting details updated",
        "meeting.cancelled": "Meeting cancelled",
        "project.created": "New project created",
        "project.updated": "Project status updated",
        "vote.cast": "Vote cast in election",
        "notification.sent": "Notification sent to user",
        "test.ping": "Test webhook event"
    }

    return {"events": events}