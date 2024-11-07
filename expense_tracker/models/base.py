# expense_tracker/models/base.py
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models"""

    # This will automatically create table names from class names
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # Common columns that will be present in all tables
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"


class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps to a model.

    This mixin provides two attributes: `created_at` and `updated_at`, which are
    automatically set to the current timestamp when a record is created or updated.
    """
    # Use server_default=func.now() to let the database handle timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
