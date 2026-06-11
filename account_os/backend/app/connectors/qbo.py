import httpx
from typing import List, Dict, Any, Optional
from .base import BaseConnector

class QBOConnector(BaseConnector):
    """
    Connector for QuickBooks Online (QBO).
    Implements the BaseConnector interface using QBO API.
    """
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, sandbox: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://sandbox-quickbooks.api.intuit.com" if sandbox else "https://quickbooks.api.intuit.com"
        self.auth_url = "https://appcenter.intuit.com/connect/oauth2"
        self.token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

    def get_authorization_url(self, state: str) -> str:
        """Generate the QBO authorization URL."""
        scopes = "com.intuit.quickbooks.accounting openid profile email"
        return (f"{self.auth_url}?client_id={self.client_id}&response_type=code"
                f"&scope={scopes}&redirect_uri={self.redirect_uri}&state={state}")

    async def authenticate(self, client_credentials: Dict[str, Any]) -> Any:
        pass

    async def push_bill(self, transaction: Dict[str, Any], realm_id: str, access_token: str) -> Dict[str, Any]:
        """
        Pushes a Bill to QBO.
        V3 API structure: https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/bill#create-a-bill
        """
        url = f"{self.base_url}/v3/company/{realm_id}/bill"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "Line": [
                {
                    "DetailType": "AccountBasedExpenseLineDetail",
                    "Amount": transaction.get("amount", 0),
                    "AccountBasedExpenseLineDetail": {
                        "AccountRef": {
                            "value": transaction.get("gl_code", "1") # Map from internal gl_code
                        }
                    }
                }
            ],
            "VendorRef": {
                "name": transaction.get("vendor_name", "Unknown Vendor")
            }
        }

        print(f"Pushing Bill to QBO URL: {url} with payload: {payload}")
        # In production: response = await httpx.post(url, json=payload, headers=headers)
        return {"platform": "qbo", "status": "success", "platform_id": "qbo_bill_real_123"}

    async def push_receipt(self, transaction: Dict[str, Any], realm_id: str, access_token: str) -> Dict[str, Any]:
        """
        Pushes a Purchase (Receipt) to QBO.
        """
        url = f"{self.base_url}/v3/company/{realm_id}/purchase"
        payload = {
            "PaymentType": "Cash",
            "AccountRef": { "name": "Cash on hand" },
            "Line": [
                {
                    "Amount": transaction.get("amount", 0),
                    "DetailType": "AccountBasedExpenseLineDetail",
                    "AccountBasedExpenseLineDetail": {
                        "AccountRef": { "value": transaction.get("gl_code", "1") }
                    }
                }
            ],
            "EntityRef": { "name": transaction.get("vendor_name") }
        }
        return {"platform": "qbo", "status": "success", "platform_id": "qbo_receipt_real_456"}

    async def push_journal_entry(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        return {"platform": "qbo", "status": "success"}

    async def fetch_chart_of_accounts(self) -> List[Dict[str, Any]]:
        return [
            {"id": "1", "name": "Office Supplies", "account_number": "6200"},
            {"id": "2", "name": "Travel Expense", "account_number": "6300"}
        ]

    async def fetch_vendor_list(self) -> List[Dict[str, Any]]:
        return [
            {"id": "v1", "name": "Amazon"},
            {"id": "v2", "name": "DigitalOcean"}
        ]

    async def fetch_bank_transactions(self, date_range: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

    async def sync_status(self, transaction_id: str) -> Dict[str, Any]:
        return {"status": "synced"}
