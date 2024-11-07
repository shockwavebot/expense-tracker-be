# expense_tracker/models/user.py
from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from expense_tracker.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    # Import only for type checking to avoid circular dependencies
    from .expense import Expense


class User(Base, TimestampMixin):
    """
    User model representing application users.

    Columns:
        id (UUID): Primary key, automatically generated
        email (str): User's email address, must be unique
        username (str): User's username
        created_at (datetime): When the user was created
        updated_at (datetime): When the user was last updated

    Relationships:
        expenses: All expenses created by this user
        shared_expenses: All expenses shared with this user
    """
    # Columns with their constraints
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,  # No two users can have the same email
        nullable=False  # Email is required
    )
    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Relationships
    expenses: Mapped[List["Expense"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"  # If user is deleted, delete their expenses
    )
