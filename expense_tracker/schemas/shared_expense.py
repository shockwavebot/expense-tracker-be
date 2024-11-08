# expense_tracker/schemas/shared_expense.py
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field

from .base import BaseSchema
from .expense import ExpenseResponse
from .user import UserResponse


class SharedExpenseStatus(str):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SETTLED = "settled"


class SharedExpenseBase(BaseSchema):
    """Base schema for shared expense data"""
    expense_id: uuid.UUID
    shared_with_user_id: uuid.UUID
    split_percentage: Decimal = Field(
        ge=0,  # Greater than or equal to 0
        le=100,  # Less than or equal to 100
        decimal_places=2
    )
    status: SharedExpenseStatus = SharedExpenseStatus.PENDING


class SharedExpenseCreate(BaseSchema):
    """Schema for creating a new shared expense"""
    shared_with_user_id: uuid.UUID
    split_percentage: Decimal = Field(ge=0, le=100, decimal_places=2)


class SharedExpenseUpdate(BaseSchema):
    """Schema for updating a shared expense"""
    status: Optional[SharedExpenseStatus] = None
    split_percentage: Optional[Decimal] = Field(
        None, ge=0, le=100, decimal_places=2)


class SharedExpenseInDB(SharedExpenseBase):
    """Schema for shared expense data from database"""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class SharedExpenseResponse(SharedExpenseInDB):
    """Schema for shared expense response with related data"""
    expense: ExpenseResponse
    shared_with_user: UserResponse
