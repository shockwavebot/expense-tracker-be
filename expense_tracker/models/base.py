from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column

from expense_tracker.db.base import Base


class TimestampedBase(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False
    )
