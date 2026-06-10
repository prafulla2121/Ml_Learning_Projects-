import pytest
from account_os.backend.app.agents.specialists import IntakeAgent, CodingAgent
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.fixture
def mock_llm_call():
    with patch("account_os.backend.app.agents.specialists.ChatOpenAI") as mock_llm_cls:
        instance = mock_llm_cls.return_value
        instance.ainvoke = AsyncMock()
        yield instance

@pytest.mark.asyncio
async def test_intake_agent_extraction(mock_llm_call):
    mock_response = {
        "vendor_name": "Amazon",
        "amount": 45.99,
        "currency": "USD",
        "transaction_date": "2026-06-10",
        "document_type": "receipt"
    }
    mock_llm_call.ainvoke.return_value = mock_response

    agent = IntakeAgent()
    result = await agent.process_document("Receipt from Amazon for $45.99 on June 10, 2026")

    assert result["vendor_name"] == "Amazon"
    assert result["amount"] == 45.99
    assert result["document_type"] == "receipt"

@pytest.mark.asyncio
async def test_coding_agent_suggestion(mock_llm_call):
    mock_response = {"gl_code": "6200", "confidence": 0.95}
    mock_llm_call.ainvoke.return_value = mock_response

    agent = CodingAgent()
    coa = [{"id": "1", "name": "Office Supplies", "account_number": "6200"}]
    transaction = {"vendor_name": "Amazon", "amount": 45.99}

    result = await agent.suggest_gl_code(transaction, coa)

    assert result["gl_code"] == "6200"
    assert result["confidence"] == 0.95
