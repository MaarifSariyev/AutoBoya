from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class VehicleBrandBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = None
    country: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class VehicleBrandCreate(VehicleBrandBase):
    pass


class VehicleBrandUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None


class VehicleBrandOut(VehicleBrandBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
