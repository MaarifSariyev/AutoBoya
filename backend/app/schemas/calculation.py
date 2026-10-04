from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class CalculationRequest(BaseModel):
    target_amount: Decimal = Field(..., gt=0, description="Target formula quantity to prepare")
    unit: str = Field(default="g", description="Unit of measurement, e.g. g or kg")


class CalculatedComponent(BaseModel):
    component_code: str
    component_name: str
    amount: Decimal = Field(..., description="Proportional amount of component")
    cumulative_amount: Decimal = Field(..., description="Running cumulative amount for scale weighing")
    percentage: Decimal = Field(..., description="Percentage of total formula")
    unit: str
    sort_order: int
    notes: Optional[str] = None


class CalculationResponse(BaseModel):
    formula_id: int
    formula_name: str
    variant_name: str
    version: int
    color_code: str
    color_name: str
    brand_name: Optional[str] = None
    model_name: Optional[str] = None
    target_amount: Decimal
    base_total_amount: Decimal
    unit: str
    factor: Decimal
    components: List[CalculatedComponent]
    total: Decimal
