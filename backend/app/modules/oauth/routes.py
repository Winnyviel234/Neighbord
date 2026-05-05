"""
OAuth2/SSO routes for external authentication
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse

from app.core.security import get_current_user, require_role
from app.core.supabase import table
from app.modules.oauth.models import OAuthLoginRequest, OAuthCallbackResponse
from app.modules.oauth.service import oauth_service
from app.core.config import settings


router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/providers")
async def get_oauth_providers():
    """Get available OAuth providers"""
    providers = []
    for name, provider in oauth_service.providers.items():
        if provider.enabled:
            providers.append({
                "name": name,
                "enabled": True
            })

    return {"providers": providers}


@router.post("/login")
async def initiate_oauth_login(request: OAuthLoginRequest):
    """Initiate OAuth login flow"""
    try:
        provider = oauth_service.get_provider(request.provider)
        if not provider:
            raise HTTPException(status_code=400, detail=f"OAuth provider '{request.provider}' not available")

        # Get frontend URL for callback
        frontend_url = settings.frontend_url.rstrip('/')
        authorization_url = oauth_service.get_authorization_url(request.provider, frontend_url)

        return {
            "authorization_url": authorization_url,
            "provider": request.provider
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate OAuth login: {str(e)}")


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None)
):
    """Handle OAuth callback from provider"""
    try:
        if error:
            # OAuth error from provider
            error_msg = error_description or error
            frontend_url = settings.frontend_url.rstrip('/')
            return RedirectResponse(
                url=f"{frontend_url}/login?error=oauth_error&message={error_msg}",
                status_code=302
            )

        # Process OAuth callback
        result = await oauth_service.handle_oauth_callback(
            provider=provider,
            code=code,
            state=state,
            redirect_uri=settings.frontend_url
        )

        if not result.success:
            frontend_url = settings.frontend_url.rstrip('/')
            return RedirectResponse(
                url=f"{frontend_url}/login?error=oauth_failed&message={result.message}",
                status_code=302
            )

        # Success - redirect to frontend with token
        # In a real implementation, you'd set an HTTP-only cookie or use a session
        frontend_url = settings.frontend_url.rstrip('/')
        redirect_url = f"{frontend_url}{result.redirect_uri}?oauth_success=true"

        if result.is_new_user:
            redirect_url += "&new_user=true"

        return RedirectResponse(url=redirect_url, status_code=302)

    except Exception as e:
        frontend_url = settings.frontend_url.rstrip('/')
        return RedirectResponse(
            url=f"{frontend_url}/login?error=server_error&message=OAuth processing failed",
            status_code=302
        )


@router.get("/user/providers")
async def get_user_oauth_providers(
    current_user: dict = Depends(get_current_user)
):
    """Get OAuth providers linked to current user"""
    try:
        result = table("oauth_accounts").select("provider, linked_at, last_used").eq("user_id", current_user["id"]).execute()

        providers = []
        for account in result.data:
            providers.append({
                "provider": account["provider"],
                "linked_at": account["linked_at"],
                "last_used": account["last_used"]
            })

        return {"linked_providers": providers}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get linked providers: {str(e)}")


@router.delete("/user/providers/{provider}")
async def unlink_oauth_provider(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """Unlink OAuth provider from current user"""
    try:
        result = table("oauth_accounts").delete().eq("user_id", current_user["id"]).eq("provider", provider).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="OAuth provider not linked")

        return {"message": f"Successfully unlinked {provider} account"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unlink provider: {str(e)}")


# Admin endpoints for OAuth configuration
@router.get("/admin/config")
async def get_oauth_config(
    current_user: dict = Depends(require_role("admin"))
):
    """Get OAuth configuration (Admin only)"""
    try:
        config = {}
        for name, provider in oauth_service.providers.items():
            config[name] = {
                "enabled": provider.enabled,
                "client_id_configured": bool(provider.client_id),
                "authorization_url": provider.authorization_url,
                "scope": provider.scope
            }

        return {"oauth_config": config}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get OAuth config: {str(e)}")


@router.put("/admin/config/{provider}")
async def update_oauth_provider(
    provider: str,
    enabled: bool,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    current_user: dict = Depends(require_role("admin"))
):
    """Update OAuth provider configuration (Admin only)"""
    try:
        if provider not in oauth_service.providers:
            raise HTTPException(status_code=404, detail="OAuth provider not found")

        # Update provider configuration
        oauth_service.providers[provider].enabled = enabled
        if client_id:
            oauth_service.providers[provider].client_id = client_id
        if client_secret:
            oauth_service.providers[provider].client_secret = client_secret

        return {"message": f"Successfully updated {provider} configuration"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update provider: {str(e)}")