import pytest
from account_os.backend.app.agents.specialists import CodingAgent
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_coding_agent_learning_loop_priority():
    coa = [{"id": "1", "name": "Office Supplies", "account_number": "6200"}]
    transaction = {"vendor_name": "Amazon", "amount": 45.99}

    # Historical correction that should take priority
    corrections = [
        {"vendor_name": "Amazon", "corrected_gl_code": "9999"}
    ]

    with patch("account_os.backend.app.agents.specialists.ChatOpenAI"):
        agent = CodingAgent()
        result = await agent.suggest_gl_code(transaction, coa, corrections)

        assert result["gl_code"] == "9999"
        assert result["confidence"] == 1.0
        assert result["source"] == "learning_loop"

@pytest.mark.asyncio
async def test_coding_agent_fallback_to_ai():
    coa = [{"id": "1", "name": "Office Supplies", "account_number": "6200"}]
    transaction = {"vendor_name": "NewVendor", "amount": 10.00}
    corrections = []

    mock_response = {"gl_code": "6200", "confidence": 0.8}

    with patch("account_os.backend.app.agents.specialists.ChatOpenAI") as mock_llm_cls:
        instance = mock_llm_cls.return_value
        instance.ainvoke = AsyncMock(return_value=mock_response)

        with patch.dict("os.environ", {"OPENAI_API_KEY": "fake_key"}):
            agent = CodingAgent()
            result = await agent.suggest_gl_code(transaction, coa, corrections)

            assert result["gl_code"] == "6200"
        assert result["source"] == "ai_suggestion"
