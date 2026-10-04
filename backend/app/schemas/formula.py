from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.formula import FormulaStatus, FormulaSourceType
from app.schemas.component import FormulaComponentCreate, FormulaComponentOut


class FormulaBase(BaseModel):
    color_id: int
    formula_name: str = Field(..., min_length=1, max_length=150)
    variant_name: str = Field(default="Standard", max_length=50)
    paint_system: str = Field(default="Basecoat", max_length=50)
    base_total_amount: Decimal = Field(default=Decimal("1000.0000"), gt=0, decimal_places=4)
    unit: str = Field(default="g", max_length=20)
    status: FormulaStatus = FormulaStatus.DRAFT
    version: int = 1
    source_type: FormulaSourceType = FormulaSourceType.EXPERT_CREATED
    expert_notes: Optional[str] = None
    preparation_notes: Optional[str] = None


class FormulaCreate(FormulaBase):
    components: List[FormulaComponentCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_components_and_total(self):
        if self.components:
            for idx, comp in enumerate(self.components):
                if comp.amount <= 0:
                    raise ValueError(f"Component at row {idx+1} ({comp.component_code}) has non-positive amount: {comp.amount}. Amounts must be positive.")
            
            calculated_sum = sum(comp.amount for comp in self.components)
            # If status is published or verified, total must strictly match
            if self.status in [FormulaStatus.VERIFIED, FormulaStatus.PUBLISHED]:
                # Allow tiny rounding within 0.0001
                if abs(calculated_sum - self.base_total_amount) > Decimal("0.001"):
                    raise ValueError(
                        f"Component amounts sum to {calculated_sum} {self.unit}, which does not match base_total_amount {self.base_total_amount} {self.unit}."
                    )
            # Auto-align base_total_amount to calculated_sum if base_total_amount is default 1000 and sum differs in draft
            elif self.status == FormulaStatus.DRAFT and self.base_total_amount == Decimal("1000.0000") and calculated_sum > 0:
                self.base_total_amount = calculated_sum
        return self


class FormulaUpdate(BaseModel):
    formula_name: Optional[str] = Field(None, min_length=1, max_length=150)
    variant_name: Optional[str] = None
    paint_system: Optional[str] = None
    base_total_amount: Optional[Decimal] = Field(None, gt=0, decimal_places=4)
    unit: Optional[str] = None
    status: Optional[FormulaStatus] = None
    source_type: Optional[FormulaSourceType] = None
    expert_notes: Optional[str] = None
    preparation_notes: Optional[str] = None
    components: Optional[List[FormulaComponentCreate]] = None


class FormulaOut(FormulaBase):
    id: int
    created_by: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    components: List[FormulaComponentOut] = []

    # Associated color/vehicle info for display
    brand_name: Optional[str] = None
    model_name: Optional[str] = None
    color_code: Optional[str] = None
    color_name: Optional[str] = None
    color_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FormulaSummaryOut(BaseModel):
    id: int
    color_id: int
    formula_name: str
    variant_name: str
    paint_system: str
    base_total_amount: Decimal
    unit: str
    status: FormulaStatus
    version: int
    source_type: FormulaSourceType
    brand_name: Optional[str] = None
    model_name: Optional[str] = None
    color_code: Optional[str] = None
    color_name: Optional[str] = None
    color_type: Optional[str] = None
    components_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
