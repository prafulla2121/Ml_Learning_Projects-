from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..agents.workflow import SyncAgent
from ..connectors.qbo import QBOConnector
from ..connectors.sage import SageConnector
from ..connectors.linnworks import LinnworksConnector
from ..db.database import get_db_context
from sqlalchemy import text
import os

router = APIRouter(prefix="/sync", tags=["sync"])

# Mocking config
QBO_CLIENT_ID = os.getenv("QBO_CLIENT_ID", "mock_id")
QBO_CLIENT_SECRET = os.getenv("QBO_CLIENT_SECRET", "mock_secret")
QBO_REDIRECT_URI = "http://localhost:3000/callback"

from .auth import get_current_user_email
from fastapi import Depends

@router.post("/{platform}/{transaction_id}")
async def sync_to_platform(platform: str, transaction_id: str, transaction_data: Dict[str, Any], email: str = Depends(get_current_user_email)):
    """
    Manually triggers the SyncAgent to push a validated transaction to an accounting platform.
    """
    if platform.lower() == "qbo":
        connector = QBOConnector(QBO_CLIENT_ID, QBO_CLIENT_SECRET, QBO_REDIRECT_URI)
        sync_agent = SyncAgent(connectors={"qbo": connector})

        # Resolve client and fetch credentials
        async with get_db_context(user_email=email) as db:
            res = await db.execute(text("SELECT client_id FROM transactions WHERE id = :tid"), {"tid": transaction_id})
            client_id = res.scalar()

            cred_res = await db.execute(
                text("SELECT encrypted_data FROM credentials WHERE client_id = :cid AND platform = 'qbo'"),
                {"cid": client_id}
            )
            row = cred_res.fetchone()
            if row:
                from ..engine.security import EncryptionService
                creds = EncryptionService.decrypt_data(row[0])
                realm_id = creds.get("realm_id")
                access_token = creds.get("access_token")
            else:
                realm_id = "mock_realm"
                access_token = "mock_token"

        try:
            result = await connector.push_bill(transaction_data, realm_id=realm_id, access_token=access_token)
            # Update status in DB on success
            async with get_db_context(user_email=email) as db:
                await db.execute(
                    text("UPDATE transactions SET status = 'synced' WHERE id = :id"),
                    {"id": transaction_id}
                )
                await db.commit()
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif platform.lower() == "sage":
        connector = SageConnector(api_key="mock_key")
        try:
            result = await connector.push_bill(transaction_data)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif platform.lower() == "linnworks":
        connector = LinnworksConnector(token="mock_token")
        try:
            result = await connector.push_bill(transaction_data)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"status": "error", "message": f"Platform {platform} not supported yet"}
