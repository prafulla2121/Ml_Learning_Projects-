import pytest
from account_os.backend.app.agents.reconciliation import ReconciliationAgent

@pytest.mark.asyncio
async def test_reconciliation_exact_match():
    agent = ReconciliationAgent()
    bank_tx = [{"id": "b1", "amount": 100.0, "vendor": "Amazon"}]
    acc_tx = [{"id": "a1", "amount": 100.0, "vendor": "Amazon.com"}]

    result = await agent.match_transactions(bank_tx, acc_tx)

    assert len(result["matches"]) == 1
    assert result["matches"][0]["bank_transaction"]["id"] == "b1"
    assert result["matches"][0]["accounting_entry"]["id"] == "a1"
    assert len(result["unmatched_bank"]) == 0
    assert len(result["unmatched_accounting"]) == 0

@pytest.mark.asyncio
async def test_reconciliation_no_match():
    agent = ReconciliationAgent()
    bank_tx = [{"id": "b1", "amount": 100.0, "vendor": "Amazon"}]
    acc_tx = [{"id": "a1", "amount": 150.0, "vendor": "Amazon.com"}]

    result = await agent.match_transactions(bank_tx, acc_tx)

    assert len(result["matches"]) == 0
    assert len(result["unmatched_bank"]) == 1
    assert len(result["unmatched_accounting"]) == 1
