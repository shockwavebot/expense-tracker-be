# expense_tracker/models/category.py
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    # Import only for type checking to avoid circular dependencies
    from .expense import Expense
    from .user import User


class Category(Base, TimestampMixin):
    """
    Category model for expense categorization.

    This model allows both system-defined categories (user_id is null)
    and user-defined custom categories.

    Columns:
        id (UUID): Primary key
        name (str): Category name (e.g., "Groceries", "Entertainment")
        user_id (UUID, optional): The user who created this category (null for system categories)
        created_at (datetime): When the category was created
        updated_at (datetime): When the category was last updated

    Relationships:
        user: The user who created this category (if any)
        expenses: All expenses in this category
    """

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    # Optional user_id for custom categories
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=True  # Null means it's a system category
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        back_populates="categories"
    )
    expenses: Mapped[List["Expense"]] = relationship(
        back_populates="category"
    )
