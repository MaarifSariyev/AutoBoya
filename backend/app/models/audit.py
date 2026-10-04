from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_email = Column(String(150), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, VERIFY, PUBLISH, DEPRECATE, IMPORT
    entity = Column(String(50), nullable=False, index=True)  # Formula, Color, Brand, Model, ComponentLibrary
    entity_id = Column(String(50), nullable=False, index=True)
    old_value = Column(Text, nullable=True)  # JSON formatted representation
    new_value = Column(Text, nullable=True)  # JSON formatted representation
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
