"""The local sign-in token works only when local development enables it."""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from tiendita.api.auth import get_current_user_id


def bearer(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def test_dev_token_accepted_in_local_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TIENDITA_DEV_AUTH", "1")
    monkeypatch.delenv("NEON_AUTH_JWKS_URL", raising=False)
    assert get_current_user_id(bearer("dev-token:Ana@galileo.edu")) == "local-ana@galileo.edu"


def test_dev_token_rejected_without_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TIENDITA_DEV_AUTH", raising=False)
    monkeypatch.delenv("NEON_AUTH_JWKS_URL", raising=False)
    with pytest.raises(HTTPException):
        get_current_user_id(bearer("dev-token:ana@galileo.edu"))


def test_dev_token_rejected_when_jwks_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TIENDITA_DEV_AUTH", "1")
    monkeypatch.setenv("NEON_AUTH_JWKS_URL", "http://127.0.0.1:9/.well-known/jwks.json")
    with pytest.raises(HTTPException) as err:
        get_current_user_id(bearer("dev-token:ana@galileo.edu"))
    assert err.value.status_code == 401
