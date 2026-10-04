"""Owner authentication: OAuth2 password flow with JWT bearer tokens, following
FastAPI's "OAuth2 with Password (and hashing), Bearer with JWT tokens" tutorial.

There is one account (the owner), configured in .env — no users table, no
sign-up. Generate its values with:

    python -c "from pwdlib import PasswordHash; print(PasswordHash.recommended().hash('your-password'))"
    python -c "import secrets; print(secrets.token_hex(32))"
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core import config

password_hash = PasswordHash.recommended()

# Verified against when the username is wrong, so a failed login takes the
# same time whether or not the username exists.
DUMMY_HASH = password_hash.hash("dummy-password")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def auth_is_configured() -> bool:
    return bool(config.AUTH_USERNAME and config.AUTH_PASSWORD_HASH and config.JWT_SECRET_KEY)


def authenticate_owner(username: str, password: str) -> bool:
    if not auth_is_configured():
        return False
    username_ok = secrets.compare_digest(username.encode(), config.AUTH_USERNAME.encode())
    hashed = config.AUTH_PASSWORD_HASH if username_ok else DUMMY_HASH
    password_ok = password_hash.verify(password, hashed)
    return username_ok and password_ok


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """Dependency for protected routes. Returns the username from a valid token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not auth_is_configured():
        raise credentials_exception
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    except InvalidTokenError:
        raise credentials_exception
    username = payload.get("sub")
    if username != config.AUTH_USERNAME:
        raise credentials_exception
    return username


CurrentUser = Annotated[str, Depends(get_current_user)]
