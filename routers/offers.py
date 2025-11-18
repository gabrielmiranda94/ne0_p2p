import asyncio
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict

from services import hodlhodl_service, market_data_service
from schemas.offer_schema import Offer

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/api/payment-methods", response_model=List[Dict], summary="Lista todos os métodos de pagamento")
async def get_payment_methods():
    """Retorna uma lista de todos os métodos de pagamento disponíveis na plataforma."""
    try:
        methods = await hodlhodl_service.get_all_payment_methods()
        return methods
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _calculate_premium(offer_price_str: str, market_price: float) -> float | None:
    try:
        offer_price = float(str(offer_price_str).replace(",", ""))
        if market_price > 0:
            premium = ((offer_price / market_price) - 1) * 100
            return round(premium, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return None
    return None

async def _get_and_process_offers(
        currency_code: str,
        payment_method: str | None,
        side: str
) -> List[dict]:

    results = await asyncio.gather(
        hodlhodl_service.get_hodlhodl_offers(
            currency_code, payment_method, side
        ),
        market_data_service.get_btc_market_price(currency_code)
    )
    raw_offers, market_price = results[0], results[1]

    processed_offers = hodlhodl_service.process_and_enrich_offers(raw_offers)

    if market_price:
        for offer in processed_offers:
            offer["market_price"] = market_price
            offer["premium"] = _calculate_premium(offer["price"], market_price)

    return processed_offers

def _parse_offers_safely(offers_data: List[dict]) -> List[Offer]:
    valid_offers = []
    for offer_dict in offers_data:
        try:
            valid_offers.append(Offer.model_validate(offer_dict))
        except Exception:
            continue
    return valid_offers

@router.get("/", response_class=HTMLResponse, summary="Página principal com as ofertas")
async def get_offers_page(request: Request):
    return templates.TemplateResponse("offers.html", {"request": request})

@router.get("/api/offers", response_model=List[Offer], summary="Endpoint de dados das ofertas")
async def api_get_offers(
        currency_code: str = Query("EUR", description="Código da moeda (EUR, BRL, USD)"),
        payment_method: str = Query(None, description="Filtra por método de pagamento"),
        side: str = Query("SELL", description="Tipo de oferta: BUY ou SELL")
):
    """Retorna uma lista de ofertas em formato JSON, filtradas primariamente por moeda."""
    try:
        processed_offers = await _get_and_process_offers(
            currency_code, payment_method, side
        )
        offers = _parse_offers_safely(processed_offers)
        return offers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))