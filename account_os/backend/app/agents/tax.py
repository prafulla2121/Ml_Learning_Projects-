from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
import os

class TaxComplianceAgent:
    """
    Agent responsible for regional tax validation (GST/VAT/Sales Tax).
    """
    def __init__(self, model: str = "gpt-4o-mini"):
        if os.getenv("OPENAI_API_KEY"):
            self.llm = ChatOpenAI(model=model, temperature=0)
        else:
            self.llm = None
        self.parser = JsonOutputParser()

    async def validate_tax(self, transaction: Dict[str, Any], tax_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validates the tax amount in a transaction against regional rules.
        """
        if not self.llm:
            # Mock logic for validation
            amount = transaction.get("amount", 0)
            return {
                "tax_is_valid": True,
                "calculated_tax": amount * 0.05, # Assuming 5% mock tax
                "applied_rate": "5%",
                "message": "Tax validated (mock)"
            }

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a tax compliance expert. Validate if the tax amount in the given transaction is correct according to the provided rules. Return JSON with 'tax_is_valid' (boolean), 'calculated_tax' (float), 'applied_rate' (string), and 'message' (string)."),
            ("user", "Transaction: {transaction}\n\nTax Rules: {rules}")
        ])

        try:
            response = await self.llm.ainvoke(prompt.format_messages(
                transaction=json.dumps(transaction),
                rules=json.dumps(tax_rules)
            ))
            return self.parser.parse(response.content) if hasattr(response, 'content') else response
        except Exception as e:
            print(f"Error in TaxComplianceAgent: {e}")
            return {"tax_is_valid": False, "error": str(e)}
