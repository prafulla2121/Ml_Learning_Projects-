import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from ..engine.currency import CurrencyEngine

class IntakeAgent:
    """
    Agent responsible for document classification and data extraction.
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        import os
        if os.getenv("OPENAI_API_KEY"):
            self.llm = ChatOpenAI(model=model, temperature=0)
        else:
            self.llm = None
        self.parser = JsonOutputParser()

    async def process_document(self, text_content: str) -> Dict[str, Any]:
        """
        Extracts structured data from raw text content.
        """
        if not self.llm:
            return {
                "vendor_name": "Mock Vendor",
                "amount": 100.0,
                "currency": "USD",
                "transaction_date": "2026-06-11",
                "document_type": "bill"
            }
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert accounting intake assistant. Extract the following fields from the document text in JSON format: vendor_name, amount, currency, transaction_date, and document_type (bill or receipt)."),
            ("user", "{text}")
        ])

        try:
            response = await self.llm.ainvoke(prompt.format_messages(text=text_content))
            result = self.parser.parse(response.content) if hasattr(response, 'content') else response
            return result
        except Exception as e:
            print(f"Error in IntakeAgent: {e}")
            return {
                "vendor_name": "Unknown",
                "amount": 0.0,
                "currency": "USD",
                "document_type": "unknown"
            }

class CodingAgent:
    """
    Agent responsible for mapping transactions to GL accounts.
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        import os
        if os.getenv("OPENAI_API_KEY"):
            self.llm = ChatOpenAI(model=model, temperature=0)
        else:
            self.llm = None
        self.parser = JsonOutputParser()
        self.currency_engine = CurrencyEngine()

    async def suggest_gl_code(self, transaction: Dict[str, Any], chart_of_accounts: List[Dict[str, Any]], corrections: Optional[List[Dict[str, Any]]] = None, target_currency: str = "USD") -> Dict[str, Any]:
        """
        Suggests a GL code based on transaction data, chart of accounts, and historical corrections.
        """
        # 0. Handle Currency Conversion if needed
        base_currency = transaction.get("currency", "USD")
        if base_currency != target_currency:
            conversion = await self.currency_engine.convert_amount(transaction["amount"], base_currency, target_currency)
            transaction["converted_data"] = conversion

        # 1. Check Learning Loop (Historical Corrections)
        vendor = transaction.get("vendor_name", "").lower()
        if corrections:
            for corr in corrections:
                if corr.get("vendor_name", "").lower() == vendor:
                    return {
                        "gl_code": corr["corrected_gl_code"],
                        "confidence": 1.0,
                        "source": "learning_loop"
                    }

        # 2. Fallback to LLM Suggestion
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert accountant. Given a transaction and a Chart of Accounts, suggest the most appropriate GL account. Return JSON with 'gl_code' and 'confidence'."),
            ("user", "Transaction: {transaction}\n\nChart of Accounts: {coa}")
        ])

        if not self.llm:
            return {"gl_code": "6000-Mock", "confidence": 0.9, "source": "mock_suggestion"}
        try:
            response = await self.llm.ainvoke(prompt.format_messages(transaction=json.dumps(transaction), coa=json.dumps(chart_of_accounts)))
            result = self.parser.parse(response.content) if hasattr(response, 'content') else response
            result["source"] = "ai_suggestion"
            return result
        except Exception as e:
            print(f"Error in CodingAgent: {e}")
            return {"gl_code": "Uncategorized", "confidence": 0, "source": "error"}
