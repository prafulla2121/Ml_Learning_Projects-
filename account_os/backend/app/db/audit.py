from typing import Dict, Any, Optional
from sqlalchemy import text
from .database import get_db_context
import json

class AuditLogger:
    """
    Utility for recording agent decisions and API actions.
    """
    @staticmethod
    async def log_action(
        client_id: str,
        action: str,
        user_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Inserts an audit log entry into the database.
        """
        async with get_db_context() as db:
            await db.execute(
                text("INSERT INTO audit_logs (client_id, user_id, action, entity_type, entity_id, details) VALUES (:client_id, :user_id, :action, :entity_type, :entity_id, :details)"),
                {
                    "client_id": client_id,
                    "user_id": user_id,
                    "action": action,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "details": json.dumps(details) if details else None
                }
            )
            await db.commit()
