# expense_tracker/models/shared_expense.py
import enum
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    # Import only for type checking to avoid circular dependencies
    from .expense import Expense
    from .user import User


class SharedExpenseStatus(enum.Enum):
    """Possible statuses for a shared expense"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SETTLED = "settled"


class SharedExpense(Base, TimestampMixin):
    """
    SharedExpense model for tracking how expenses are shared between users.

    Columns:
        id (UUID): Primary key
        expense_id (UUID): The expense being shared
        shared_with_user_id (UUID): The user this expense is shared with
        split_percentage (Decimal): What percentage of the expense this user should pay
        status (SharedExpenseStatus): Current status of this shared expense
        created_at (datetime): When the sharing was created
        updated_at (datetime): When the sharing was last updated

    Relationships:
        expense: The expense being shared
        shared_with_user: The user this expense is shared with
    """
    __tablename__ = "shared_expense"

    # Foreign keys
    expense_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("expense.id", ondelete="CASCADE"),
        nullable=False
    )
    shared_with_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    # Other fields
    split_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),  # 5 digits total, 2 decimal places (e.g., 33.33)
        nullable=False
    )
    status: Mapped[SharedExpenseStatus] = mapped_column(
        SQLEnum(SharedExpenseStatus),
        nullable=False,
        default=SharedExpenseStatus.PENDING
    )

    # Relationships
    expense: Mapped["Expense"] = relationship(
        back_populates="shared_expenses"
    )
    shared_with_user: Mapped["User"] = relationship(
        back_populates="shared_with_me"
    )
