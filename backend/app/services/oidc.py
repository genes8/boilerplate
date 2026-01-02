"""OIDC (OpenID Connect) service for SSO authentication."""

from typing import Any
from urllib.parse import urlencode

import httpx
from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwt
from authlib.oidc.core import CodeIDToken

from app.config import settings


class OIDCService:
    """
    OIDC service for handling OpenID Connect authentication.

    Supports providers like:
    - Keycloak
    - Azure AD
    - Google
    - Okta
    - Auth0
    """

    def __init__(self) -> None:
        """Initialize OIDC service."""
        self.oauth = OAuth()
        self._provider_config: dict[str, Any] | None = None

        if settings.oidc_configured:
            self._configure_provider()

    def _configure_provider(self) -> None:
        """Configure OIDC provider."""
        self.oauth.register(
            name="oidc",
            client_id=settings.OIDC_CLIENT_ID,
            client_secret=settings.OIDC_CLIENT_SECRET,
            server_metadata_url=f"{settings.OIDC_ISSUER_URL}/.well-known/openid-configuration",
            client_kwargs={
                "scope": "openid email profile",
            },
        )

    async def get_provider_config(self) -> dict[str, Any]:
        """
        Fetch OIDC provider configuration from well-known endpoint.

        Returns:
            dict: Provider configuration.
        """
        if self._provider_config is not None:
            return self._provider_config

        if not settings.OIDC_ISSUER_URL:
            raise ValueError("OIDC_ISSUER_URL is not configured")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.OIDC_ISSUER_URL}/.well-known/openid-configuration"
            )
            response.raise_for_status()
            self._provider_config = response.json()

        return self._provider_config

    def get_authorization_url(self, state: str, nonce: str) -> str:
        """
        Generate authorization URL for OIDC login.

        Args:
            state: Random state for CSRF protection.
            nonce: Random nonce for replay protection.

        Returns:
            str: Authorization URL to redirect user to.
        """
        if not settings.oidc_configured:
            raise ValueError("OIDC is not configured")

        params = {
            "client_id": settings.OIDC_CLIENT_ID,
            "redirect_uri": settings.OIDC_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "nonce": nonce,
        }

        # Build authorization URL
        # This will be replaced with actual URL from provider config
        auth_endpoint = f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/auth"

        return f"{auth_endpoint}?{urlencode(params)}"

    async def exchange_code_for_tokens(
        self, code: str, state: str
    ) -> dict[str, Any]:
        """
        Exchange authorization code for tokens.

        Args:
            code: Authorization code from callback.
            state: State parameter for verification.

        Returns:
            dict: Token response containing access_token, id_token, etc.
        """
        if not settings.oidc_configured:
            raise ValueError("OIDC is not configured")

        config = await self.get_provider_config()
        token_endpoint = config.get("token_endpoint")

        if not token_endpoint:
            raise ValueError("Token endpoint not found in provider config")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_endpoint,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.OIDC_REDIRECT_URI,
                    "client_id": settings.OIDC_CLIENT_ID,
                    "client_secret": settings.OIDC_CLIENT_SECRET,
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """
        Get user information from OIDC provider.

        Args:
            access_token: Access token from token exchange.

        Returns:
            dict: User information from provider.
        """
        config = await self.get_provider_config()
        userinfo_endpoint = config.get("userinfo_endpoint")

        if not userinfo_endpoint:
            raise ValueError("Userinfo endpoint not found in provider config")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                userinfo_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    def decode_id_token(
        self, id_token: str, nonce: str | None = None
    ) -> dict[str, Any]:
        """
        Decode and validate ID token.

        Args:
            id_token: ID token from token exchange.
            nonce: Expected nonce for validation.

        Returns:
            dict: Decoded ID token claims.
        """
        # In production, you should verify the token signature
        # using the provider's public keys (JWKS)
        claims = jwt.decode(id_token, claims_cls=CodeIDToken)

        # Validate claims
        claims.validate()

        if nonce and claims.get("nonce") != nonce:
            raise ValueError("Invalid nonce in ID token")

        return dict(claims)

    def extract_user_info(self, token_response: dict[str, Any]) -> dict[str, Any]:
        """
        Extract user information from token response.

        Args:
            token_response: Response from token exchange.

        Returns:
            dict: Extracted user information.
        """
        id_token = token_response.get("id_token")

        if not id_token:
            raise ValueError("No ID token in response")

        # Decode ID token (without full validation for now)
        # In production, implement proper JWT validation
        import base64
        import json

        # Split token and decode payload
        parts = id_token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid ID token format")

        # Decode payload (add padding if needed)
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding

        claims = json.loads(base64.urlsafe_b64decode(payload))

        return {
            "sub": claims.get("sub"),
            "email": claims.get("email"),
            "email_verified": claims.get("email_verified", False),
            "name": claims.get("name"),
            "preferred_username": claims.get("preferred_username"),
            "given_name": claims.get("given_name"),
            "family_name": claims.get("family_name"),
            "issuer": claims.get("iss"),
        }


# Global OIDC service instance
oidc_service = OIDCService()
