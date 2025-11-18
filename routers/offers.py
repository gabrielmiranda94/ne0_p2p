import asyncio  # 1. Importar a biblioteca asyncio
import datetime
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List

from services import hodlhodl_service, market_data_service
from schemas.offer_schema import Offer

router = APIRouter()
templates = Jinja2Templates(directory="templates")

COUNTRY_CURRENCY_MAP = {
    "PT": "EUR",
    "BR": "BRL",
    "US": "USD",
}

def _calculate_premium(offer_price_str: str, market_price: float) -> float | None:
    try:
        offer_price = float(offer_price_str.replace(",", ""))
        if market_price > 0:
            premium = ((offer_price / market_price) - 1) * 100
            return round(premium, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return None
    return None

async def _get_and_process_offers(country_code: str, payment_method: str | None) -> List[dict]:
    """
    Função centralizada para buscar ofertas e enriquecê-las com dados de mercado.
    """
    currency = COUNTRY_CURRENCY_MAP.get(country_code.upper(), "USD")

    # 2. AQUI ESTÁ A CORREÇÃO: Usar asyncio.gather para executar ambas em paralelo
    results = await asyncio.gather(
        hodlhodl_service.get_hodlhodl_offers(country_code, payment_method),
        market_data_service.get_btc_market_price(currency)
    )
    raw_offers, market_price = results[0], results[1]

    processed_offers = hodlhodl_service.process_and_enrich_offers(raw_offers)

    if market_price:
        for offer in processed_offers:
            offer["market_price"] = market_price
            offer["premium"] = _calculate_premium(offer["price"], market_price)

    return processed_offers

def _parse_offers_safely(offers_data: List[dict]) -> List[Offer]:
    """Helper para parsear ofertas, ignorando as que falham na validação."""
    valid_offers = []
    for offer_dict in offers_data:
        try:
            # Atenção: Usando model_validate em vez de parse_obj para compatibilidade Pydantic v2
            valid_offers.append(Offer.model_validate(offer_dict))
        except Exception:
            continue
    return valid_offers

@router.get("/", response_class=HTMLResponse, summary="Página principal com as ofertas")
async def get_offers_page(
        request: Request,
        country: str = Query("PT", description="Código do país (PT, BR, US)")
):
    """Renderiza a página HTML que exibe as ofertas."""
    processed_offers = await _get_and_process_offers(country, None)
    offers = _parse_offers_safely(processed_offers)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "offers": offers,
        "selected_country": country,
        "current_year": datetime.datetime.now().year,
    })

@router.get("/api/offers", response_model=List[Offer], summary="Endpoint de dados das ofertas")
async def api_get_offers(
        country_code: str = Query("PT", description="Código do país (PT, BR, US)"),
        payment_method: str = Query(None, description="Filtra por método de pagamento")
):
    """Retorna uma lista de ofertas em formato JSON, enriquecida com dados de mercado."""
    try:
        processed_offers = await _get_and_process_offers(country_code, payment_method)
        offers = _parse_offers_safely(processed_offers)
        return offers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
