from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseConnector(ABC):
    @abstractmethod
    async def authenticate(self, client_credentials: Dict[str, Any]) -> Any:
        """Authenticate with the platform."""
        pass

    @abstractmethod
    async def push_bill(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Push a bill to the platform."""
        pass

    @abstractmethod
    async def push_receipt(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Push a receipt to the platform."""
        pass

    @abstractmethod
    async def push_journal_entry(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Push a journal entry to the platform."""
        pass

    @abstractmethod
    async def fetch_chart_of_accounts(self) -> List[Dict[str, Any]]:
        """Fetch the chart of accounts from the platform."""
        pass

    @abstractmethod
    async def fetch_vendor_list(self) -> List[Dict[str, Any]]:
        """Fetch the vendor list from the platform."""
        pass

    @abstractmethod
    async def fetch_bank_transactions(self, date_range: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch bank transactions from the platform."""
        pass

    @abstractmethod
    async def sync_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check the status of a synced transaction."""
        pass
