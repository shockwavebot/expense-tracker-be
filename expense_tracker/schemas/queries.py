# expense_tracker/schemas/queries.py
import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import Field

from .base import BaseSchema


class ExpenseFilter(BaseSchema):
    """Schema for filtering expenses"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category_id: Optional[List[uuid.UUID]] = None
    min_amount: Optional[Decimal] = Field(None, ge=0)
    max_amount: Optional[Decimal] = Field(None, ge=0)
    description_contains: Optional[str] = None
    shared_only: Optional[bool] = False


class ExpenseAnalytics(BaseSchema):
    """Schema for expense analytics response"""
    total_amount: Decimal
    average_amount: Decimal
    category_breakdown: List[dict[str, Decimal]]
    monthly_totals: List[dict[str, Decimal]]
