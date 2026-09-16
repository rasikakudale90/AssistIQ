from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from backend.models.governance import AuditLog


class AuditRepository:
    @staticmethod
    def create_log(
        db: Session,
        action: str,
        target_type: str,
        target_id: str,
        actor_id: Optional[str] = None,
        before_value: Optional[Dict[str, Any]] = None,
        after_value: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Appends an immutable audit log entry in the current transaction (SRS §5.11).
        """
        audit_entry = AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            before_value=before_value,
            after_value=after_value,
        )
        db.add(audit_entry)
        # We do not commit here — committed as part of the caller's atomic transaction
        return audit_entry

    @staticmethod
    def get_timeline_for_target(
        db: Session,
        target_type: str,
        target_id: str,
    ) -> List[AuditLog]:
        """
        Retrieves full chronological audit history for a specific entity.
        """
        return (
            db.query(AuditLog)
            .filter(AuditLog.target_type == target_type, AuditLog.target_id == target_id)
            .order_by(AuditLog.created_at.asc())
            .all()
        )
