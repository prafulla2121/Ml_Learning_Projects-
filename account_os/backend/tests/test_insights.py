import pytest
from account_os.backend.app.agents.insights import InsightsAgent

@pytest.mark.asyncio
async def test_insights_agent_duplicate_detection():
    agent = InsightsAgent()
    transactions = [
        {"vendor_name": "Amazon", "amount": 100.0, "transaction_date": "2026-06-10"},
        {"vendor_name": "Amazon", "amount": 100.0, "transaction_date": "2026-06-10"},
    ]

    insights = await agent.analyze_transactions(transactions)

    assert len(insights) == 1
    assert insights[0]["type"] == "anomaly"
    assert "Duplicate" in insights[0]["title"]

@pytest.mark.asyncio
async def test_insights_agent_high_value_detection():
    agent = InsightsAgent()
    transactions = [
        {"vendor_name": "Tesla", "amount": 50000.0, "transaction_date": "2026-06-10"},
    ]

    insights = await agent.analyze_transactions(transactions)

    assert len(insights) == 1
    assert "High Value" in insights[0]["title"]
