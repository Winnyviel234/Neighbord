import time
from fastapi import APIRouter
from app.core.config import settings
from app.core.cache import cache

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
start_time = time.time()


@router.get("/status")
def status():
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "uptime_seconds": int(time.time() - start_time),
        "redis_enabled": cache.redis_enabled,
        "cache_backend": "redis" if cache.redis_enabled else "memory",
        "elasticsearch_enabled": bool(settings.elasticsearch_url.strip()),
        "whatsapp_enabled": bool(
            settings.twilio_account_sid.strip()
            and settings.twilio_auth_token.strip()
            and settings.twilio_from_number.strip()
        ),
    }
