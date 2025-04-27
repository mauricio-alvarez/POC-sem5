from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_session
from app.features.auth.models import *
from app.features.auth.schemas import *
from app.features.auth.services import *

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(get_session)])

@router.post("/signup")
async def create_user(user: SignupRequest) -> SignupResponse:
    """Register a new user."""

    try:
        response: SignupResponse = signup_service(user)
        return response
    except HTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error
    except Exception as error:
        print(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed",
        ) from error


@router.post("/login")
async def login(user: LoginRequest) -> LoginResponse:
    """Login a user."""
    try:
        response: LoginResponse = login_service(user)
        return response
    except HTTPException as error:
        raise error
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500, detail="Internal server error") from error