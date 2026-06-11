import pytest
from account_os.backend.app.agents.ar_automation import ARAgent
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_ar_agent_overdue_detection():
    agent = ARAgent()
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    invoices = [
        {"id": "1", "customer_name": "C1", "amount": 100, "due_date": yesterday, "status": "sent"},
        {"id": "2", "customer_name": "C2", "amount": 200, "due_date": tomorrow, "status": "sent"},
        {"id": "3", "customer_name": "C3", "amount": 300, "due_date": yesterday, "status": "paid"},
    ]

    overdue = await agent.identify_overdue_invoices(invoices)

    assert len(overdue) == 1
    assert overdue[0]["id"] == "1"

@pytest.mark.asyncio
async def test_ar_agent_reminder_generation():
    agent = ARAgent()
    overdue = [{"id": "1", "customer_name": "C1", "amount": 100}]

    tasks = await agent.generate_reminder_tasks(overdue)

    assert len(tasks) == 1
    assert tasks[0]["reminder_type"] == "email"
    assert "C1" in tasks[0]["template"]
