from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        # Username can only contain alphanumeric characters, underscores, and hyphens
        # No @ symbol or other special characters allowed
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        if '@' in v:
            raise ValueError('Username cannot contain @ symbol. Please use only letters, numbers, underscores, and hyphens')
        return v


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
