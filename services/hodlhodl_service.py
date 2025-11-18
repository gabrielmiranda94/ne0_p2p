import httpx
import os
from typing import List

# Vamos manter a URL base e adicionar o novo endpoint
HODLHODL_BASE_URL = "https://hodlhodl.com"
AFFILIATE_CODE = os.getenv("AFFILIATE_CODE", "ne0_p2p")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}

# Esta é a mudança principal: vamos usar a API privada /frontend/
async def get_hodlhodl_offers(
        currency_code: str,
        payment_method: str | None,
        side: str,
        sort_by: str,
        sort_direction: str
) -> List[dict]:
    """Busca ofertas da API /frontend/ da Hodl Hodl, permitindo busca global por moeda."""

    # Parâmetros para a API /frontend/
    params = {
        "filters[side]": side,
        "filters[currency_code]": currency_code.upper(),
        "pagination[limit]": 50,
        "pagination[offset]": 0,
        # A API /frontend/ não parece suportar ordenação, então removemos esses parâmetros por agora
        # "sort[by]": sort_by,
        # "sort[direction]": sort_direction,
    }

    if payment_method:
        params["filters[payment_method_name]"] = payment_method

    async with httpx.AsyncClient(base_url=HODLHODL_BASE_URL, headers=HEADERS, verify=False) as client:
        try:
            # Apontamos para o novo endpoint
            response = await client.get("/api/frontend/offers", params=params)
            response.raise_for_status()
            # A estrutura da resposta da API /frontend/ pode ser diferente
            data = response.json()
            offers = data.get("offers", [])
            print(f"HODL HODL /frontend/ API: Sucesso! Recebidas {len(offers)} ofertas.")
            return offers
        except httpx.HTTPStatusError as e:
            print(f"HODL HODL API: Erro de status HTTP: {e.response.status_code} - {e.request.url}")
            return []
        except httpx.RequestError as e:
            print(f"HODL HODL API: Erro de conexão: {e}")
            return []

# A função process_and_enrich_offers continua igual.
def process_and_enrich_offers(offers: List[dict]) -> List[dict]:
    enriched_offers = []
    for offer in offers:
        try:
            pm_name = "N/A"
            # A estrutura da API /frontend/ pode ser diferente
            payment_methods = offer.get("payment_methods", [])
            if payment_methods:
                pm_name = payment_methods[0].get("name")

            trader_info = offer.get("trader", {})
            rating = trader_info.get("rating")
            trader_rating = float(rating) if rating is not None else 0.0

            processed_offer = {
                "id": offer.get("id"),
                "asset_code": offer.get("asset_code"),
                "side": offer.get("side"),
                "description": offer.get("description"),
                "price": offer.get("price"),
                "min_amount": offer.get("min_amount"),
                "max_amount": offer.get("max_amount"),
                "country": offer.get("country_code"), # API /frontend/ usa country_code
                "payment_method_name": pm_name,
                "trader_username": trader_info.get("login"),
                "trader_rating": trader_rating,
                "affiliate_link": f"https://hodlhodl.com/offers/{offer.get('id')}?ref={AFFILIATE_CODE}"
            }
            enriched_offers.append(processed_offer)
        except (KeyError, TypeError, IndexError, ValueError):
            continue
    return enriched_offers