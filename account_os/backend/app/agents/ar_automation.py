from typing import List, Dict, Any
from datetime import datetime, timedelta

class ARAgent:
    """
    Agent responsible for Accounts Receivable automation.
    Handles invoice tracking and reminder logic.
    """
    async def identify_overdue_invoices(self, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identifies invoices that are past their due date and not yet paid.
        """
        overdue = []
        today = datetime.now().date()

        for inv in invoices:
            due_date = inv.get("due_date")
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

            if inv["status"] != "paid" and due_date < today:
                overdue.append(inv)

        return overdue

    async def generate_reminder_tasks(self, overdue_invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generates reminder tasks (email/whatsapp) for overdue invoices.
        """
        tasks = []
        for inv in overdue_invoices:
            tasks.append({
                "invoice_id": inv["id"],
                "customer": inv["customer_name"],
                "amount": inv["amount"],
                "reminder_type": "email",
                "template": f"Dear {inv['customer_name']}, your invoice for {inv['amount']} is overdue."
            })
        return tasks
