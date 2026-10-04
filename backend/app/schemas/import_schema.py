from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ImportRow(BaseModel):
    row_number: int
    brand: str
    model: Optional[str] = None
    year: Optional[int] = None
    color_code: str
    color_name: str
    color_type: str = "Metallic"
    paint_system: str = "Basecoat"
    variant: str = "Standard"
    component_code: str
    component_name: str
    amount: Decimal
    unit: str = "g"
    status: str = "DRAFT"
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ImportPreviewResponse(BaseModel):
    batch_id: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    total_formulas_detected: int
    errors: List[str] = Field(default_factory=list)
    sample_preview: List[ImportRow]
    can_proceed: bool


class ImportConfirmRequest(BaseModel):
    batch_id: str


class ImportResultResponse(BaseModel):
    brands_created: int
    models_created: int
    colors_created: int
    formulas_created: int
    components_created: int
    message: str
