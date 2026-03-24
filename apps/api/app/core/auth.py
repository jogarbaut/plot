from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.config import settings

_security = HTTPBearer()


@lru_cache
def get_jwks_client() -> PyJWKClient:
    return PyJWKClient(f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json")


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
    jwks_client: PyJWKClient = Depends(get_jwks_client),
) -> dict:
    """FastAPI dependency — verifies the Auth0 JWT and returns the decoded payload.

    Usage:
        @router.get("/me")
        def get_me(token: dict = Depends(verify_token)):
            user_id = token["sub"]
    """
    token = credentials.credentials
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=settings.AUTH0_ALGORITHMS,
            audience=settings.AUTH0_AUDIENCE,
            issuer=f"https://{settings.AUTH0_DOMAIN}/",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
