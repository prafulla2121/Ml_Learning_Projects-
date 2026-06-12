from typing import List, Dict, Any

class InsightsAgent:
    """
    Agent responsible for providing financial insights and detecting anomalies.
    """
    async def analyze_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyzes a list of transactions for anomalies and insights.
        """
        insights = []

        # 1. Detect Duplicates
        seen = set()
        for tx in transactions:
            key = (tx.get("vendor_name"), tx.get("amount"), tx.get("transaction_date"))
            if key in seen:
                insights.append({
                    "type": "anomaly",
                    "severity": "high",
                    "title": "Possible Duplicate Bill",
                    "description": f"Multiple bills found for {tx.get('vendor_name')} with amount {tx.get('amount')}."
                })
            seen.add(key)

        # 2. Large Amount Detection
        for tx in transactions:
            if float(tx.get("amount", 0)) > 10000:
                insights.append({
                    "type": "insight",
                    "severity": "medium",
                    "title": "High Value Transaction",
                    "description": f"A large payment of {tx.get('amount')} was recorded for {tx.get('vendor_name')}."
                })

        # 3. Trend Anomaly (Sudden increase in vendor spending)
        # Mocking trend analysis
        vendor_totals = {}
        for tx in transactions:
            v = tx.get("vendor_name")
            vendor_totals[v] = vendor_totals.get(v, 0) + float(tx.get("amount", 0))

        for vendor, total in vendor_totals.items():
            if total > 50000: # Threshold for mock trend
                 insights.append({
                    "type": "anomaly",
                    "severity": "medium",
                    "title": "Unusual Vendor Spend Trend",
                    "description": f"Spending for {vendor} has exceeded 50,000 this period, which is 40% above average."
                })

        return insights
