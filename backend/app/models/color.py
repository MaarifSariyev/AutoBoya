import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class ColorType(str, enum.Enum):
    SOLID = "Solid"
    METALLIC = "Metallic"
    PEARL = "Pearl"
    MATTE = "Matte"
    CANDY = "Candy"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class Color(Base):
    __tablename__ = "colors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("vehicle_brands.id", ondelete="CASCADE"), nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("vehicle_models.id", ondelete="SET NULL"), nullable=True, index=True)
    color_code = Column(String(50), nullable=False, index=True)
    color_name = Column(String(100), nullable=False, index=True)
    color_type = Column(Enum(ColorType, name="color_type_enum"), default=ColorType.METALLIC, nullable=False)
    paint_system = Column(String(50), default="Basecoat", nullable=False, index=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("brand_id", "color_code", "paint_system", name="uq_brand_color_system"),
    )

    # Relationships
    brand = relationship("VehicleBrand", back_populates="colors")
    model = relationship("VehicleModel", back_populates="colors")
    formulas = relationship("Formula", back_populates="color", cascade="all, delete-orphan")
