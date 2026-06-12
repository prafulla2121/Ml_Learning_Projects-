from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..agents.workflow import SyncAgent
from ..connectors.qbo import QBOConnector
from ..connectors.sage import SageConnector
from ..connectors.linnworks import LinnworksConnector
import os

router = APIRouter(prefix="/sync", tags=["sync"])

# Mocking config
QBO_CLIENT_ID = os.getenv("QBO_CLIENT_ID", "mock_id")
QBO_CLIENT_SECRET = os.getenv("QBO_CLIENT_SECRET", "mock_secret")
QBO_REDIRECT_URI = "http://localhost:3000/callback"

@router.post("/{platform}/{transaction_id}")
async def sync_to_platform(platform: str, transaction_id: str, transaction_data: Dict[str, Any]):
    """
    Manually triggers the SyncAgent to push a validated transaction to an accounting platform.
    """
    if platform.lower() == "qbo":
        connector = QBOConnector(QBO_CLIENT_ID, QBO_CLIENT_SECRET, QBO_REDIRECT_URI)
        sync_agent = SyncAgent(connectors={"qbo": connector})

        try:
            result = await connector.push_bill(transaction_data)
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
