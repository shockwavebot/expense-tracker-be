from datetime import datetime

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None, max_length=255)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=255)


class CategoryInDBBase(CategoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Category(CategoryInDBBase):
    pass
