from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class VehicleModelBase(BaseModel):
    brand_id: int
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    is_active: bool = True


class VehicleModelCreate(VehicleModelBase):
    pass


class VehicleModelUpdate(BaseModel):
    brand_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    is_active: Optional[bool] = None


class VehicleModelOut(VehicleModelBase):
    id: int
    slug: str
    brand_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
