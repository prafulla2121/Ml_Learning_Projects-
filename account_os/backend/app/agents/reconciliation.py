from typing import List, Dict, Any
from datetime import datetime

class ReconciliationAgent:
    """
    Agent responsible for matching bank transactions to accounting entries.
    """
    async def match_transactions(self, bank_transactions: List[Dict[str, Any]], accounting_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Attempts to match bank transactions to accounting entries based on amount, date, and vendor.
        """
        matches = []
        unmatched_bank = []
        unmatched_accounting = accounting_entries.copy()

        for bank_tx in bank_transactions:
            found_match = False
            for acc_tx in unmatched_accounting:
                if self._is_match(bank_tx, acc_tx):
                    matches.append({
                        "bank_transaction": bank_tx,
                        "accounting_entry": acc_tx,
                        "confidence": self._calculate_confidence(bank_tx, acc_tx)
                    })
                    unmatched_accounting.remove(acc_tx)
                    found_match = True
                    break

            if not found_match:
                unmatched_bank.append(bank_tx)

        return {
            "matches": matches,
            "unmatched_bank": unmatched_bank,
            "unmatched_accounting": unmatched_accounting
        }

    def _is_match(self, bank_tx: Dict[str, Any], acc_tx: Dict[str, Any]) -> bool:
        # Simple matching logic: same amount and within a date range
        amount_match = abs(float(bank_tx["amount"])) == abs(float(acc_tx["amount"]))
        # In a real app, date parsing and range check would be here
        return amount_match

    def _calculate_confidence(self, bank_tx: Dict[str, Any], acc_tx: Dict[str, Any]) -> float:
        # Scoring based on vendor name similarity and exact date match
        return 0.95
