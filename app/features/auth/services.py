"""Services for users."""

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token, get_password_hash

from .models import User
from .repository import (
  create_user as repository_create_user,
)
from .repository import (
  get_user as repository_get_user,
)
from .schemas import Token, UserCreate, UserCreateResponse
from .utils import authenticate_user


def register(user_schema: UserCreate) -> UserCreateResponse:
  """Register a new user."""
  user: User = User(**user_schema.model_dump())
  if repository_get_user(user.email):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Email already registered",
    )
  user.password = get_password_hash(user.password)
  repository_create_user(user)
  if user.id is None:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="User not created",
    )
  return UserCreateResponse(id=user.id)


def login(form_data: OAuth2PasswordRequestForm) -> Token:
  """Login a user."""
  user: User | None = authenticate_user(form_data.username, form_data.password)
  if user is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect username or password",
      headers={"WWW-Authenticate": "Bearer"},
    )
  access_token = create_access_token(data={"sub": user.email})
  return Token(access_token=access_token, token_type="bearer")
