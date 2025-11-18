import httpx
import os
from typing import List

# Constantes que definem como conectar à API
HODLHODL_API_URL = "https://hodlhodl.com/api"
AFFILIATE_CODE = os.getenv("AFFILIATE_CODE", "ne0_p2p")

async def get_hodlhodl_offers(
        country_code: str,
        payment_method: str | None,
        side: str = "SELL"
) -> List[dict]:
    """Busca ofertas da API da Hodl Hodl com filtros."""

    params = {
        "filters[side]": side,
        "filters[asset_code]": "BTC",
        "filters[country_code]": country_code.upper(),
        "filters[online]": "true",
        "pagination[limit]": 50,
        "pagination[offset]": 0,
    }
    if payment_method:
        params["filters[payment_method_name]"] = payment_method

    async with httpx.AsyncClient(base_url=HODLHODL_API_URL) as client:
        try:
            response = await client.get("/v1/offers", params=params)
            response.raise_for_status()
            return response.json().get("offers", [])
        except (httpx.RequestError, httpx.HTTPStatusError):
            return []

def process_and_enrich_offers(offers: List[dict]) -> List[dict]:
    """Processa a lista de ofertas cruas e adiciona o link de afiliado."""
    enriched_offers = []
    for offer in offers:
        try:
            processed_offer = {
                "id": offer.get("id"),
                "asset_code": offer.get("asset_code"),
                "side": offer.get("side"),
                "description": offer.get("description"),
                "price": offer.get("price"),
                "min_amount": offer.get("min_amount"),
                "max_amount": offer.get("max_amount"),
                "country": offer.get("country"),
                "payment_method_name": offer.get("payment_method_name"),
                "trader_username": offer.get("trader", {}).get("login"),
                "trader_rating": offer.get("trader", {}).get("rating"),
                "affiliate_link": f"https://hodlhodl.com/offers/{offer.get('id')}?ref={AFFILIATE_CODE}"
            }
            enriched_offers.append(processed_offer)
        except (KeyError, TypeError):
            continue
    return enriched_offers