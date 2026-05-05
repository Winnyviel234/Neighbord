"""
OAuth2/SSO models for external authentication
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class OAuthProvider(BaseModel):
    """OAuth provider configuration"""
    name: str  # google, github, facebook, etc.
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    user_info_url: str
    scope: str
    enabled: bool = True


class OAuthState(BaseModel):
    """OAuth state for CSRF protection"""
    state: str
    provider: str
    redirect_uri: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime


class OAuthToken(BaseModel):
    """OAuth token response"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int]
    refresh_token: Optional[str]
    scope: Optional[str]


class OAuthUserInfo(BaseModel):
    """Standardized user info from OAuth providers"""
    provider: str
    provider_id: str
    email: str
    name: str
    first_name: Optional[str]
    last_name: Optional[str]
    avatar_url: Optional[str]
    raw_data: Dict[str, Any]  # Original provider response


class OAuthAccount(BaseModel):
    """Linked OAuth account for existing users"""
    id: str
    user_id: str
    provider: str
    provider_id: str
    email: str
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_expires_at: Optional[datetime]
    linked_at: datetime
    last_used: Optional[datetime]


class OAuthLoginRequest(BaseModel):
    """OAuth login initiation request"""
    provider: str
    redirect_uri: str = "/dashboard"


class OAuthCallbackResponse(BaseModel):
    """OAuth callback response"""
    success: bool
    user_id: Optional[str]
    is_new_user: bool = False
    redirect_uri: str
    message: str