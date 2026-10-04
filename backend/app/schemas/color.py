from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.color import ColorType


class ColorBase(BaseModel):
    brand_id: int
    model_id: Optional[int] = None
    color_code: str = Field(..., min_length=1, max_length=50)
    color_name: str = Field(..., min_length=1, max_length=100)
    color_type: ColorType = ColorType.METALLIC
    paint_system: str = Field(default="Basecoat", max_length=50)
    notes: Optional[str] = None
    is_active: bool = True


class ColorCreate(ColorBase):
    pass


class ColorUpdate(BaseModel):
    brand_id: Optional[int] = None
    model_id: Optional[int] = None
    color_code: Optional[str] = Field(None, min_length=1, max_length=50)
    color_name: Optional[str] = Field(None, min_length=1, max_length=100)
    color_type: Optional[ColorType] = None
    paint_system: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ColorOut(ColorBase):
    id: int
    brand_name: Optional[str] = None
    model_name: Optional[str] = None
    formulas_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
