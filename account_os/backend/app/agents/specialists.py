import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class IntakeAgent:
    """
    Agent responsible for document classification and data extraction.
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.parser = JsonOutputParser()

    async def process_document(self, text_content: str) -> Dict[str, Any]:
        """
        Extracts structured data from raw text content.
        """
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
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.parser = JsonOutputParser()

    async def suggest_gl_code(self, transaction: Dict[str, Any], chart_of_accounts: List[Dict[str, Any]], corrections: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Suggests a GL code based on transaction data, chart of accounts, and historical corrections.
        """
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

        try:
            response = await self.llm.ainvoke(prompt.format_messages(transaction=json.dumps(transaction), coa=json.dumps(chart_of_accounts)))
            result = self.parser.parse(response.content) if hasattr(response, 'content') else response
            result["source"] = "ai_suggestion"
            return result
        except Exception as e:
            print(f"Error in CodingAgent: {e}")
            return {"gl_code": "Uncategorized", "confidence": 0, "source": "error"}
