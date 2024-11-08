# expense_tracker/models/expense.py
import uuid
from datetime import date as dt_date  # Pylance workaround
from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    # Import only for type checking to avoid circular dependencies
    from .category import Category
    from .shared_expense import SharedExpense
    from .user import User


class Expense(Base, TimestampMixin):
    """
    Expense model representing individual expenses.

    Columns:
        id (UUID): Primary key
        user_id (UUID): Who created this expense
        category_id (UUID): Which category this expense belongs to
        amount (Decimal): How much money was spent
        description (str): What the expense was for
        date (date): When the expense occurred
        created_at (datetime): When the record was created
        updated_at (datetime): When the record was last updated

    Relationships:
        user: Who created this expense
        category: What category this belongs to
        shared_expenses: Records of how this expense is shared with others
    """

    # Required fields
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),  # 10 digits total, 2 decimal places
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    date: Mapped[dt_date] = mapped_column(
        Date,
        nullable=False
    )

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        # Prevent category deletion if has expenses
        ForeignKey("category.id", ondelete="RESTRICT"),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="expenses"
    )
    category: Mapped["Category"] = relationship(
        back_populates="expenses"
    )
    shared_expenses: Mapped[List["SharedExpense"]] = relationship(
        back_populates="expense",
        cascade="all, delete-orphan"
    )
