from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.auth import verify_token

VALID_PAYLOAD = {"sub": "auth0|123", "aud": "https://api.plot.app"}


def _make_credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def _make_jwks_client(*, raises: Exception | None = None, payload: dict = VALID_PAYLOAD) -> MagicMock:
    client = MagicMock()
    signing_key = MagicMock()
    signing_key.key = "fake-key"

    if raises:
        client.get_signing_key_from_jwt.side_effect = raises
    else:
        client.get_signing_key_from_jwt.return_value = signing_key

    return client


describe_verify_token = "verify_token"


class TestVerifyToken:
    def test_returns_decoded_payload_for_valid_token(self, monkeypatch):
        jwks_client = _make_jwks_client()
        monkeypatch.setattr(
            "app.core.auth.jwt.decode",
            lambda *args, **kwargs: VALID_PAYLOAD,
        )

        result = verify_token(
            credentials=_make_credentials("valid.token.here"),
            jwks_client=jwks_client,
        )

        assert result == VALID_PAYLOAD

    def test_raises_401_for_expired_token(self, monkeypatch):
        jwks_client = _make_jwks_client()
        monkeypatch.setattr(
            "app.core.auth.jwt.decode",
            MagicMock(side_effect=jwt.ExpiredSignatureError),
        )

        with pytest.raises(HTTPException) as exc:
            verify_token(
                credentials=_make_credentials("expired.token.here"),
                jwks_client=jwks_client,
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Token expired"

    def test_raises_401_for_invalid_token(self, monkeypatch):
        jwks_client = _make_jwks_client(raises=jwt.InvalidTokenError)

        with pytest.raises(HTTPException) as exc:
            verify_token(
                credentials=_make_credentials("invalid.token.here"),
                jwks_client=jwks_client,
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Invalid token"
