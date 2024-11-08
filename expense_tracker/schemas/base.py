# expense_tracker/schemas/base.py
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configurations"""
    model_config = ConfigDict(
        from_attributes=True,  # Allows converting SQLAlchemy models to Pydantic models
        json_encoders={
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
    )
