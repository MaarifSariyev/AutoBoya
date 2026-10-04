import enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class FormulaStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    PUBLISHED = "PUBLISHED"
    DEPRECATED = "DEPRECATED"


class FormulaSourceType(str, enum.Enum):
    EXPERT_CREATED = "EXPERT_CREATED"
    MANUFACTURER = "MANUFACTURER"
    DISTRIBUTOR = "DISTRIBUTOR"
    MEASURED = "MEASURED"
    CORRECTED = "CORRECTED"
    IMPORTED = "IMPORTED"
    OTHER = "OTHER"


class Formula(Base):
    __tablename__ = "formulas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    color_id = Column(Integer, ForeignKey("colors.id", ondelete="CASCADE"), nullable=False, index=True)
    formula_name = Column(String(150), nullable=False)
    variant_name = Column(String(50), default="Standard", nullable=False, index=True)
    paint_system = Column(String(50), default="Basecoat", nullable=False)
    base_total_amount = Column(Numeric(12, 4), default=1000.0000, nullable=False)
    unit = Column(String(20), default="g", nullable=False)
    status = Column(Enum(FormulaStatus, name="formula_status_enum"), default=FormulaStatus.DRAFT, nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    source_type = Column(Enum(FormulaSourceType, name="formula_source_type_enum"), default=FormulaSourceType.EXPERT_CREATED, nullable=False)
    expert_notes = Column(Text, nullable=True)
    preparation_notes = Column(Text, nullable=True)
    created_by = Column(String(150), nullable=True)
    verified_by = Column(String(150), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    color = relationship("Color", back_populates="formulas")
    components = relationship(
        "FormulaComponent",
        back_populates="formula",
        cascade="all, delete-orphan",
        order_by="FormulaComponent.sort_order",
    )
