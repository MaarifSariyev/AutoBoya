from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class FormulaComponent(Base):
    __tablename__ = "formula_components"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    formula_id = Column(Integer, ForeignKey("formulas.id", ondelete="CASCADE"), nullable=False, index=True)
    component_code = Column(String(50), nullable=False, index=True)
    component_name = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 4), nullable=False)
    unit = Column(String(20), default="g", nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    formula = relationship("Formula", back_populates="components")


class ComponentLibrary(Base):
    __tablename__ = "component_library"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    brand = Column(String(100), nullable=True)  # e.g., Standox, PPG, Kapci, Duxone
    category = Column(String(50), nullable=True)  # e.g., Base, Toner, Pearl, Metallic, Binder, Additive
    unit = Column(String(20), default="g", nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
