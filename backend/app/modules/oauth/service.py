"""
OAuth2/SSO service for external authentication
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import aiohttp

from app.core.cache.redis_cache import cache_manager
from app.core.supabase import table
from app.modules.oauth.models import (
    OAuthProvider, OAuthState, OAuthToken, OAuthUserInfo,
    OAuthAccount, OAuthCallbackResponse
)
from app.modules.auth.service import AuthService


class OAuthService:
    """Service for OAuth2/SSO authentication"""

    def __init__(self):
        self.auth_service = AuthService()

        # OAuth provider configurations
        self.providers = {
            "google": OAuthProvider(
                name="google",
                client_id="",  # Set via environment
                client_secret="",  # Set via environment
                authorization_url="https://accounts.google.com/o/oauth2/auth",
                token_url="https://oauth2.googleapis.com/token",
                user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
                scope="openid email profile"
            ),
            "github": OAuthProvider(
                name="github",
                client_id="",  # Set via environment
                client_secret="",  # Set via environment
                authorization_url="https://github.com/login/oauth/authorize",
                token_url="https://github.com/login/oauth/access_token",
                user_info_url="https://api.github.com/user",
                scope="user:email"
            ),
            "facebook": OAuthProvider(
                name="facebook",
                client_id="",  # Set via environment
                client_secret="",  # Set via environment
                authorization_url="https://www.facebook.com/v18.0/dialog/oauth",
                token_url="https://graph.facebook.com/v18.0/oauth/access_token",
                user_info_url="https://graph.facebook.com/me?fields=id,name,email,first_name,last_name,picture",
                scope="email,public_profile"
            )
        }

    def get_provider(self, provider_name: str) -> Optional[OAuthProvider]:
        """Get OAuth provider configuration"""
        provider = self.providers.get(provider_name)
        if not provider or not provider.enabled:
            return None

        # Override with environment variables if available
        # In a real implementation, you'd load these from settings
        return provider

    def generate_state(self, provider: str, redirect_uri: str) -> str:
        """Generate OAuth state for CSRF protection"""
        state = secrets.token_urlsafe(32)
        state_data = OAuthState(
            state=state,
            provider=provider,
            redirect_uri=redirect_uri,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )

        # Cache state for 10 minutes
        if cache_manager.enabled:
            cache_manager.set(f"oauth_state:{state}", state_data.dict(), ttl=600)

        return state

    def verify_state(self, state: str) -> Optional[OAuthState]:
        """Verify OAuth state"""
        if not cache_manager.enabled:
            return None

        state_data = cache_manager.get(f"oauth_state:{state}")
        if not state_data:
            return None

        state_obj = OAuthState(**state_data)

        # Check expiration
        if datetime.utcnow() > state_obj.expires_at:
            return None

        # Delete used state
        cache_manager.delete(f"oauth_state:{state}")

        return state_obj

    def get_authorization_url(self, provider_name: str, redirect_uri: str) -> str:
        """Get OAuth authorization URL"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"OAuth provider '{provider_name}' not configured")

        state = self.generate_state(provider_name, redirect_uri)

        params = {
            "client_id": provider.client_id,
            "redirect_uri": f"{redirect_uri}/auth/oauth/{provider_name}/callback",
            "scope": provider.scope,
            "response_type": "code",
            "state": state
        }

        # Build URL
        url = provider.authorization_url + "?"
        url += "&".join([f"{k}={v}" for k, v in params.items()])

        return url

    async def exchange_code_for_token(self, provider_name: str, code: str, redirect_uri: str) -> OAuthToken:
        """Exchange authorization code for access token"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"OAuth provider '{provider_name}' not configured")

        async with aiohttp.ClientSession() as session:
            data = {
                "client_id": provider.client_id,
                "client_secret": provider.client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{redirect_uri}/auth/oauth/{provider_name}/callback"
            }

            headers = {"Accept": "application/json"}

            async with session.post(provider.token_url, data=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"OAuth token exchange failed: {error_text}")

                token_data = await response.json()
                return OAuthToken(**token_data)

    async def get_user_info(self, provider_name: str, access_token: str) -> OAuthUserInfo:
        """Get user information from OAuth provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"OAuth provider '{provider_name}' not configured")

        headers = {"Authorization": f"Bearer {access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(provider.user_info_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"Failed to get user info: {error_text}")

                user_data = await response.json()

                # Standardize user info based on provider
                return self._standardize_user_info(provider_name, user_data)

    def _standardize_user_info(self, provider: str, data: Dict[str, Any]) -> OAuthUserInfo:
        """Standardize user info from different providers"""
        if provider == "google":
            return OAuthUserInfo(
                provider=provider,
                provider_id=data["id"],
                email=data["email"],
                name=data.get("name", ""),
                first_name=data.get("given_name"),
                last_name=data.get("family_name"),
                avatar_url=data.get("picture"),
                raw_data=data
            )
        elif provider == "github":
            return OAuthUserInfo(
                provider=provider,
                provider_id=str(data["id"]),
                email=data.get("email", ""),
                name=data.get("name", ""),
                first_name=data.get("name", "").split()[0] if data.get("name") else None,
                last_name=" ".join(data.get("name", "").split()[1:]) if data.get("name") and len(data["name"].split()) > 1 else None,
                avatar_url=data.get("avatar_url"),
                raw_data=data
            )
        elif provider == "facebook":
            return OAuthUserInfo(
                provider=provider,
                provider_id=data["id"],
                email=data.get("email", ""),
                name=data.get("name", ""),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                avatar_url=data.get("picture", {}).get("data", {}).get("url") if data.get("picture") else None,
                raw_data=data
            )
        else:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

    async def find_or_create_user(self, oauth_user: OAuthUserInfo) -> Dict[str, Any]:
        """Find existing user or create new one from OAuth data"""
        # Check if OAuth account already exists
        existing_account = table("oauth_accounts").select("*").eq("provider", oauth_user.provider).eq("provider_id", oauth_user.provider_id).execute()

        if existing_account.data:
            # Existing OAuth account - get user
            account = existing_account.data[0]
            user_result = table("users").select("*").eq("id", account["user_id"]).execute()

            if user_result.data:
                return {
                    "user": user_result.data[0],
                    "is_new_user": False,
                    "oauth_account": account
                }

        # Check if user exists by email
        user_result = table("users").select("*").eq("email", oauth_user.email).execute()

        if user_result.data:
            # Link OAuth account to existing user
            user = user_result.data[0]
            oauth_account = await self.link_oauth_account(user["id"], oauth_user)

            return {
                "user": user,
                "is_new_user": False,
                "oauth_account": oauth_account
            }

        # Create new user
        new_user = await self.auth_service.create_user_from_oauth(oauth_user)

        # Create OAuth account link
        oauth_account = await self.link_oauth_account(new_user["id"], oauth_user)

        return {
            "user": new_user,
            "is_new_user": True,
            "oauth_account": oauth_account
        }

    async def link_oauth_account(self, user_id: str, oauth_user: OAuthUserInfo, access_token: Optional[str] = None, refresh_token: Optional[str] = None) -> Dict[str, Any]:
        """Link OAuth account to existing user"""
        account_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "provider": oauth_user.provider,
            "provider_id": oauth_user.provider_id,
            "email": oauth_user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expires_at": datetime.utcnow() + timedelta(hours=1) if access_token else None,
            "linked_at": datetime.utcnow().isoformat(),
            "last_used": datetime.utcnow().isoformat()
        }

        result = table("oauth_accounts").insert(account_data).execute()
        return result.data[0]

    async def handle_oauth_callback(self, provider: str, code: str, state: str, redirect_uri: str) -> OAuthCallbackResponse:
        """Handle OAuth callback and authenticate user"""
        try:
            # Verify state
            state_data = self.verify_state(state)
            if not state_data or state_data.provider != provider:
                return OAuthCallbackResponse(
                    success=False,
                    redirect_uri=redirect_uri,
                    message="Invalid OAuth state"
                )

            # Exchange code for token
            token = await self.exchange_code_for_token(provider, code, redirect_uri)

            # Get user info
            user_info = await self.get_user_info(provider, token.access_token)

            # Find or create user
            result = await self.find_or_create_user(user_info)

            # Generate JWT token
            jwt_token = self.auth_service.create_access_token({"sub": result["user"]["id"]})

            return OAuthCallbackResponse(
                success=True,
                user_id=result["user"]["id"],
                is_new_user=result["is_new_user"],
                redirect_uri=state_data.redirect_uri,
                message="OAuth authentication successful"
            )

        except Exception as e:
            return OAuthCallbackResponse(
                success=False,
                redirect_uri=redirect_uri,
                message=f"OAuth authentication failed: {str(e)}"
            )


# Global OAuth service instance
oauth_service = OAuthService()