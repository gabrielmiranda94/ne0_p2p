import httpx
from typing import Dict

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# Mapeia as moedas do nosso site para os IDs da CoinGecko
# Podemos adicionar mais moedas aqui no futuro
CURRENCY_MAP = {
    "EUR": "eur",
    "BRL": "brl",
    "USD": "usd",
}

async def get_btc_market_price(currency: str) -> float | None:
    """
    Busca o preço de mercado atual do Bitcoin para uma moeda específica.
    Retorna o preço como um float, ou None se falhar.
    """
    coingecko_currency = CURRENCY_MAP.get(currency.upper())
    if not coingecko_currency:
        return None

    async with httpx.AsyncClient(base_url=COINGECKO_API_URL) as client:
        try:
            params = {
                "ids": "bitcoin",
                "vs_currencies": coingecko_currency,
            }
            response = await client.get("/simple/price", params=params)
            response.raise_for_status()
            data = response.json()

            # O resultado será algo como: {'bitcoin': {'eur': 50000}}
            price = data.get("bitcoin", {}).get(coingecko_currency)
            return float(price) if price else None

        except (httpx.RequestError, httpx.HTTPStatusError, KeyError, ValueError):
            return None