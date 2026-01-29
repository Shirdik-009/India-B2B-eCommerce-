"""User schemas."""
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=20)
    company_name: str | None = Field(None, max_length=255)
    role: str = Field(default="buyer", pattern="^(buyer|seller)$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str | None
    company_name: str | None
    is_verified: bool
    role: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
