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
            "top_categories": sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
        }
