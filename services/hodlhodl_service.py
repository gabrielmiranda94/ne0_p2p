import httpx
from typing import List, Dict
from core.config import settings

async def get_hodlhodl_offers(country_code: str, payment_method: str | None) -> List[Dict]:
    """
    Busca ofertas na API da Hodl Hodl e retorna os dados brutos.
    """
    filters = {
        "filters[side]": "sell",
        "filters[asset_code]": "BTC",
        "filters[country]": country_code.upper(),
        "filters[include_global]": "false",
    }
    if payment_method:
        filters[f"filters[payment_method_instruction_slugs][]"] = payment_method

    async with httpx.AsyncClient(base_url=settings.HODLHODL_API_URL) as client:
        try:
            response = await client.get("/offers", params=filters)
            response.raise_for_status()
            data = response.json()
            return data.get("offers", [])
        except (httpx.RequestError, httpx.HTTPStatusError):
            # Em uma aplicação real, aqui teríamos logs do erro
            return []

def process_and_enrich_offers(offers_data: List[Dict]) -> List[Dict]:
    """
    Processa os dados brutos, enriquece com o link de afiliado e limpa os dados.
    """
    processed_offers = []
    for offer_data in offers_data:
        try:
            enriched_data = offer_data.copy()
            enriched_data["affiliate_link"] = f"https://hodlhodl.com/offers/{offer_data['id']}/r/{settings.AFFILIATE_CODE}"
            enriched_data["trader_username"] = offer_data.get("trader", {}).get("login", "N/A")
            enriched_data["trader_rating"] = offer_data.get("trader", {}).get("average_rating", 0.0)
            processed_offers.append(enriched_data)
        except (KeyError, TypeError):
            continue
    return processed_offers