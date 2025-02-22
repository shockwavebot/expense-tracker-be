# expense_tracker/models/user.py
from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from uuid import UUID
from expense_tracker.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    # Import only for type checking to avoid circular dependencies
    from .category import Category
    from .expense import Expense
    from .shared_expense import SharedExpense


class User(SQLAlchemyBaseUserTable[UUID], Base, TimestampMixin):
    """
    Enhanced User model with auth capabilities

    Columns:
        id (UUID): Primary key, automatically generated
        email (str): User's email address, must be unique
        username (str): User's username
        created_at (datetime): When the user was created
        updated_at (datetime): When the user was last updated
        # inherited from SQLAlchemyBaseUserTable
        hashed_password (str): Hashed password for authentication
        is_active (bool): Whether the user is active
        is_superuser (bool): Whether the user is a superuser
        is_verified (bool): Whether the user has verified their email

    Relationships:
        expenses: All expenses created by this user
        shared_expenses: All expenses shared with this user
    """
    # Columns with their constraints

    # email is already defined in SQLAlchemyBaseUserTable - will this work? 
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

    categories: Mapped[List["Category"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"  # If user is deleted, delete their custom categories
    )

    shared_with_me: Mapped[List["SharedExpense"]] = relationship(
        back_populates="shared_with_user"
    )
