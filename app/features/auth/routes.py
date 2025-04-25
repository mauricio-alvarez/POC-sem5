from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.features.auth.schemas import *
from app.core.database import get_session
from .utils import current_user

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(get_session)])

@router.post("/register")
async def register(user: SignupRequest) -> SignupResponse:
  """Register a new user."""
  try:
    response: SignupResponse = service_register(user)
    return response
  except HTTPException as error:
    raise error
  except Exception as error:
    print(error)
    raise HTTPException(status_code=500, detail="Internal server error") from error


@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
  """Login a user."""
  try:
    token = service_login(form_data)
    return token
  except HTTPException as error:
    raise error
  except Exception as error:
    print(error)
    raise HTTPException(status_code=500, detail="Internal server error") from error


@router.get("/me", dependencies=[Depends(get_current_user)])
async def get_user():
  """Get a user."""
  try:
    return current_user.get()
  except HTTPException as error:
    raise error
  except Exception as error:
    print(error)
    raise HTTPException(status_code=500, detail="Internal server error") from error
