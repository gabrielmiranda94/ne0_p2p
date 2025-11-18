import httpx

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
CURRENCY_MAP = {"EUR": "eur", "BRL": "brl", "USD": "usd"}

# Adicionamos o mesmo "disfarce" aqui
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

async def get_btc_market_price(currency: str) -> float | None:
    coingecko_currency = CURRENCY_MAP.get(currency.upper())
    if not coingecko_currency:
        return None

    # Adicionamos os headers e o verify=False
    async with httpx.AsyncClient(base_url=COINGECKO_API_URL, headers=HEADERS, verify=False) as client:
        try:
            params = {"ids": "bitcoin", "vs_currencies": coingecko_currency}
            response = await client.get("/simple/price", params=params)
            response.raise_for_status()
            data = response.json()
            price = data.get("bitcoin", {}).get(coingecko_currency)
            print(f"COINGECKO API: Sucesso! Preço BTC/{currency.upper()} = {price}")
            return float(price) if price else None
        except (httpx.HTTPStatusError, httpx.RequestError, KeyError, ValueError) as e:
            print(f"COINGECKO API: Erro: {e}")
            return None