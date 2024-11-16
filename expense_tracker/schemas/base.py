# expense_tracker/schemas/base.py
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.json_schema import JsonSchemaValue


class BaseSchema(BaseModel):
    """Base schema with common configurations"""
    model_config = ConfigDict(
        from_attributes=True,
    )

    def model_dump_json(self, **kwargs: Any) -> str:
        """Override json serialization for datetime and UUID."""
        def serialize_value(v: Any) -> Any:
            if isinstance(v, datetime):
                return v.isoformat()
            if isinstance(v, uuid.UUID):
                return str(v)
            return v

        kwargs.setdefault('indent', 2)
        return super().model_dump_json(
            serialization_hook=serialize_value,
            **kwargs
        )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override dict serialization for datetime and UUID."""
        data = super().model_dump(**kwargs)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                data[key] = str(value)
        return data

    @classmethod
    def model_json_schema(cls, by_alias: bool = True, **kwargs: Any) -> JsonSchemaValue:
        """Customize JSON schema generation."""
        schema = super().model_json_schema(by_alias=by_alias, **kwargs)

        # Add custom formats for specific types
        for prop in schema.get("properties", {}).values():
            if prop.get("type") == "string" and prop.get("format") == "date-time":
                prop["example"] = "2024-03-07T12:00:00Z"
            elif prop.get("type") == "string" and prop.get("format") == "uuid":
                prop["example"] = "123e4567-e89b-12d3-a456-426614174000"

        return schema
