import logging

import jwt
from django.conf import settings
from jwt import PyJWKClient
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class ClerkJWTAuthentication(BaseAuthentication):
    """DRF authentication class that verifies Clerk session JWTs using JWKS."""

    def __init__(self):
        jwks_url = getattr(settings, "CLERK_JWKS_URL", "")
        if jwks_url:
            self.jwk_client = PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=3600)
        else:
            self.jwk_client = None
        self.authorized_parties = getattr(
            settings, "CLERK_AUTHORIZED_PARTIES", ["http://localhost:3000"]
        )

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        if not self.jwk_client:
            logger.warning("CLERK_JWKS_URL not configured, skipping JWT auth")
            return None

        token = auth_header.split(" ", 1)[1]

        try:
            signing_key = self.jwk_client.get_signing_key_from_jwt(token)

            decoded = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={
                    "verify_exp": True,
                    "verify_aud": False,
                },
            )

            azp = decoded.get("azp")
            if azp and azp not in self.authorized_parties:
                raise AuthenticationFailed(f"Invalid authorized party: {azp}")

            user = ClerkUser(decoded)
            return (user, decoded)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token: {e}")


class ClerkUser:
    """Minimal user object for DRF compatibility with Clerk JWTs."""

    def __init__(self, payload: dict):
        self.payload = payload
        self.clerk_id = payload.get("sub")
        self.session_id = payload.get("sid")
        self.org_id = payload.get("org_id")
        self.org_role = payload.get("org_role")
        self.is_authenticated = True
        self.is_active = True

    @property
    def is_anonymous(self):
        return False

    @property
    def pk(self):
        return self.clerk_id

    def __str__(self):
        return self.clerk_id or "anonymous"
