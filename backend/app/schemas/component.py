from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# Component in library
class ComponentLibraryBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    unit: str = Field(default="g", max_length=20)
    description: Optional[str] = None
    is_active: bool = True


class ComponentLibraryCreate(ComponentLibraryBase):
    pass


class ComponentLibraryUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    brand: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ComponentLibraryOut(ComponentLibraryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Formula component item
class FormulaComponentBase(BaseModel):
    component_code: str = Field(..., min_length=1, max_length=50)
    component_name: str = Field(..., min_length=1, max_length=100)
    amount: Decimal = Field(..., gt=0, decimal_places=4)
    unit: str = Field(default="g", max_length=20)
    sort_order: int = 0
    notes: Optional[str] = None


class FormulaComponentCreate(FormulaComponentBase):
    pass


class FormulaComponentOut(FormulaComponentBase):
    id: int
    formula_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
