from pydantic import BaseModel, EmailStr, Field

class LoginRequest (BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., min_length=6, description="Password of the user")

    class Config:
        extra = "forbid"

class LoginResponse (BaseModel):
    id: int = Field(..., description="Unique identifier of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    full_name: str = Field(..., description="Full name of the user")
    is_active: bool = Field(..., description="Is the user active")
    roles: list[str] = Field(..., description="Roles assigned to the user")
    token: str = Field(..., description="JWT token for authentication")

class SignupRequest (BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    full_name: str = Field(..., description="Full name of the user")
    password: str = Field(..., min_length=6, description="Password of the user")

    class Config:
        extra = "forbid"

class SignupResponse (BaseModel):
    id: int = Field(..., description="Unique identifier of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    full_name: str = Field(..., description="Full name of the user")
    is_active: bool = Field(..., description="Is the user active")
    roles: list[str] = Field(..., description="Roles assigned to the user")

class Token(BaseModel):
  """Token schema."""

  access_token: str
  token_type: str