from fastapi import HTTPException, status

from .models import *
from .schemas import *
from .repositories import (create_user as repository_create_user)
from .repositories import (get_user as repository_get_user)

def signup_service(user_schema: SignupRequest) -> SignupResponse:
    """Register a new user."""
    user: User = User(**user_schema.model_dump())
    if repository_get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    repository_create_user(user)
    if not user.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed",
        )
    return SignupResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        roles=[role.title for role in user.roles],
    )

def login_service(user_schema: LoginRequest) -> LoginResponse:
    """Login a user."""
    user: User | None = repository_get_user(user_schema.email)
    if not user or user.password != user_schema.password or user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    return LoginResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        roles=[role.title for role in user.roles],
    )