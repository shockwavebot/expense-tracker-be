from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from expense_tracker.models.base import TimestampedBase


class Category(TimestampedBase):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Use string reference to avoid circular import
    user: Mapped["User"] = relationship(
        "User", back_populates="categories"
    )
