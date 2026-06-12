from typing import List, Dict, Any

class ReportingAgent:
    """
    Agent responsible for generating financial summaries and reports.
    """
    async def generate_summary(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a basic financial summary from a list of transactions.
        """
        total_income = 0
        total_expenses = 0
        categories = {}

        for tx in transactions:
            amount = float(tx.get("amount", 0))
            if amount > 0:
                total_income += amount
            else:
                total_expenses += abs(amount)

            category = tx.get("gl_code", "Uncategorized")
            categories[category] = categories.get(category, 0) + abs(amount)

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_profit": total_income - total_expenses,
            "top_categories": [{"gl_code": k, "amount": v} for k, v in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]]
        }

    async def generate_cash_flow(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a simplified cash flow summary.
        """
        operating_inflow = 0
        operating_outflow = 0

        for tx in transactions:
            amount = float(tx.get("amount", 0))
            if amount > 0:
                operating_inflow += amount
            else:
                operating_outflow += abs(amount)

        return {
            "net_cash_flow": operating_inflow - operating_outflow,
            "inflow": operating_inflow,
            "outflow": operating_outflow
        }
