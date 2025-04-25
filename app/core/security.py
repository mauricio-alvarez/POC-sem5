"""This module contains the security configuration for the FastAPI application."""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password, hashed_password):
  """Verify the password."""
  return bcrypt.checkpw(
    bytes(plain_password, encoding="utf-8"),
    bytes(hashed_password, encoding="utf-8"),
  )


def get_password_hash(password):
  """Get the password hash."""
  return bcrypt.hashpw(
    bytes(password, encoding="utf-8"),
    bcrypt.gensalt(),
  )


def create_access_token(data: dict):
  """Create the access token."""
  to_encode = data.copy()
  expire = datetime.now(UTC) + timedelta(
    seconds=settings.JWT_EXPIRATION_DELTA_SECONDS
  )
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(
    to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
  )
  return encoded_jwt


def decode_token(token):
  """Decode token."""
  return jwt.decode(
    token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
  )
