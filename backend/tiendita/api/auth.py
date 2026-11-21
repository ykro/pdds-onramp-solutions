"""JWT verification against JWKS (local test JWKS in Step 4, Neon Auth in Step 5)."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

ALLOWED_ALGORITHMS = ["RS256", "EdDSA"]
security = HTTPBearer(auto_error=False)


@lru_cache(maxsize=4)
def get_jwk_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


def verify_jwt_token(
    token: str,
    jwks_url: str,
    issuer: str | None = None,
    audience: str | None = None,
) -> dict[str, Any]:
    """Verify JWT signature, expiration, issuer, and audience against JWKS."""
    client = get_jwk_client(jwks_url)
    signing_key = client.get_signing_key_from_jwt(token)
    decode_kwargs: dict[str, Any] = {
        "algorithms": ALLOWED_ALGORITHMS,
        "options": {"require": ["sub", "exp"]},
    }
    if issuer:
        decode_kwargs["issuer"] = issuer
    if audience:
        decode_kwargs["audience"] = audience
    else:
        decode_kwargs["options"]["verify_aud"] = False

    payload = jwt.decode(token, signing_key.key, **decode_kwargs)
    return dict(payload)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """FastAPI dependency that extracts and validates the Bearer JWT."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jwks_url = os.environ.get("NEON_AUTH_JWKS_URL", "")
    issuer = os.environ.get("JWT_ISSUER") or None
    audience = os.environ.get("JWT_AUDIENCE") or None
    if not jwks_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NEON_AUTH_JWKS_URL is not configured",
        )

    try:
        payload = verify_jwt_token(
            credentials.credentials,
            jwks_url=jwks_url,
            issuer=issuer,
            audience=audience,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )
    return sub
