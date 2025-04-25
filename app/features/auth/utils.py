"""User utils."""

from contextvars import ContextVar
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.core.security import decode_token, oauth2_scheme, verify_password

from .models import User
from .repository import get_user as repository_get_user


def authenticate_user(username: str, password: str) -> User | None:
  """Authenticate user."""
  user = repository_get_user(username)
  if user is None:
    return None

  if verify_password(password, user.password) is False:
    return None

  return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
  """Get current user."""
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  payload = decode_token(token)
  username = payload.get("sub")
  if username is None:
    raise credentials_exception
  user = repository_get_user(username)
  if user is None:
    raise credentials_exception
  context_var_token = current_user.set(user)
  try:
    yield user
  finally:
    current_user.reset(context_var_token)


current_user: ContextVar[User] = ContextVar("current_user")
