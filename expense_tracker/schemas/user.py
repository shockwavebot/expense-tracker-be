# expense_tracker/schemas/user.py
import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from .base import BaseSchema


class UserBase(BaseSchema):
    """Base schema for user data"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass


class UserUpdate(BaseSchema):
    """Schema for updating a user"""
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)


class UserInDB(UserBase):
    """Schema for user data from database"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UserResponse(UserInDB):
    """Schema for user response"""
    pass
