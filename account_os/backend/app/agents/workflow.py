from typing import Dict, Any, List
from ..connectors.qbo import QBOConnector
from ..connectors.base import BaseConnector

class SyncAgent:
    """
    Agent responsible for pushing validated transactions to accounting platforms.
    """
    def __init__(self, connectors: Dict[str, BaseConnector] = None):
        self.connectors = connectors or {}

    async def sync_transaction(self, platform: str, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Syncs a transaction to the specified platform.
        """
        connector = self.connectors.get(platform.lower())
        if not connector:
            return {"status": "error", "message": f"Connector for {platform} not found"}

        doc_type = transaction.get("document_type", "bill").lower()

        try:
            if doc_type == "bill":
                result = await connector.push_bill(transaction)
            elif doc_type == "receipt":
                result = await connector.push_receipt(transaction)
            else:
                result = await connector.push_journal_entry(transaction)

            return result
        except Exception as e:
            print(f"Error syncing to {platform}: {e}")
            return {"status": "error", "message": str(e)}

class ApprovalAgent:
    """
    Agent responsible for managing the approval workflow.
    """
    async def process_approval(self, transaction: Dict[str, Any], rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Determines if a transaction needs approval based on rules.
        """
        amount = transaction.get("amount", 0)
        vendor = transaction.get("vendor_name", "")

        needs_approval = False
        reason = ""

        for rule in rules:
            if rule.get("rule_type") == "approval":
                config = rule.get("configuration", {})
                threshold = config.get("threshold", 0)
                if amount > threshold:
                    needs_approval = True
                    reason = f"Amount {amount} exceeds threshold {threshold}"
                    break

        return {
            "needs_approval": needs_approval,
            "approval_reason": reason,
            "status": "pending_approval" if needs_approval else "ready_to_sync"
        }
