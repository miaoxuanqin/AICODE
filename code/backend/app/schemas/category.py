from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[str] = None
    level: int = 1
    description: Optional[str] = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[str] = None
    level: Optional[int] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryItem(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    level: int = 1
    description: Optional[str] = None
    sort_order: int = 0
    children: List["CategoryItem"] = []

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    level: int = 1
    description: Optional[str] = None
    sort_order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Allow recursive model
CategoryItem.model_rebuild()