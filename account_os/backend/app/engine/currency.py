from typing import Dict, Any, Optional
import httpx
import os

class CurrencyEngine:
    """
    Service for exchange rate handling and currency conversion.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("EXCHANGE_RATE_API_KEY")
        self.base_url = "https://v6.exchangerate-api.com/v6"

    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Fetches the real-time exchange rate between two currencies.
        """
        if not self.api_key:
            # Standard mock rates for common pairs if no API key
            mock_rates = {
                ("USD", "INR"): 83.5,
                ("USD", "EUR"): 0.92,
                ("GBP", "USD"): 1.27
            }
            return mock_rates.get((from_currency.upper(), to_currency.upper()), 1.0)

        url = f"{self.base_url}/{self.api_key}/pair/{from_currency}/{to_currency}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                data = response.json()
                if data.get("result") == "success":
                    return data["conversion_rate"]
                return 1.0
            except Exception as e:
                print(f"Error fetching exchange rate: {e}")
                return 1.0

    async def convert_amount(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """
        Converts an amount from one currency to another.
        """
        rate = await self.get_exchange_rate(from_currency, to_currency)
        return {
            "original_amount": amount,
            "original_currency": from_currency,
            "target_currency": to_currency,
            "converted_amount": round(amount * rate, 2),
            "exchange_rate": rate
        }
