# expense_tracker/schemas/category.py
import uuid
from datetime import datetime
from typing import Optional

from pydantic import Field

from .base import BaseSchema


class CategoryBase(BaseSchema):
    """Base schema for category data"""
    name: str = Field(..., min_length=3, max_length=50)


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class CategoryUpdate(CategoryBase):
    """Schema for updating a category"""
    name: str | None = Field(None, min_length=3, max_length=50)


class CategoryInDB(CategoryBase):
    """Schema for category data from database"""
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None  # None for system categories
    created_at: datetime
    updated_at: datetime


class CategoryResponse(CategoryInDB):
    """Schema for category response"""
    pass
