import json
from typing import Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.audit import AuditLog


class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        user_email: str,
        action: str,
        entity: str,
        entity_id: Any,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        details: Optional[str] = None,
    ) -> AuditLog:
        def serialize(val: Any) -> Optional[str]:
            if val is None:
                return None
            if isinstance(val, str):
                return val
            try:
                return json.dumps(val, default=str)
            except Exception:
                return str(val)

        log = AuditLog(
            user_email=user_email,
            action=action,
            entity=entity,
            entity_id=str(entity_id),
            old_value=serialize(old_value),
            new_value=serialize(new_value),
            details=details,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
