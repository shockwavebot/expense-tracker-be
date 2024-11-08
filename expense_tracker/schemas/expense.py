# expense_tracker/schemas/expense.py
import datetime
import uuid
from decimal import Decimal
from typing import Optional

from pydantic import Field

from .base import BaseSchema
from .category import CategoryResponse
from .user import UserResponse


class ExpenseBase(BaseSchema):
    """Base schema for expense data"""
    amount: Decimal = Field(ge=0)  # Amount must be non-negative
    description: str = Field(..., min_length=1, max_length=255)
    date: datetime.date
    category_id: uuid.UUID


class ExpenseCreate(ExpenseBase):
    """Schema for creating a new expense"""
    pass


class ExpenseUpdate(BaseSchema):
    """Schema for updating an expense"""
    amount: Optional[Decimal] = Field(None, ge=0)
    description: str | None = Field(None, min_length=1, max_length=255)

    date: Optional[datetime.date] = None
    category_id: Optional[uuid.UUID] = None


class ExpenseInDB(ExpenseBase):
    """Schema for expense data from database"""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ExpenseResponse(ExpenseInDB):
    """Schema for expense response with related data"""
    category: CategoryResponse
    user: UserResponse
