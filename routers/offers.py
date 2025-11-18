from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List

from schemas.offer_schema import Offer
from services import hodlhodl_service

# ESTA É A LINHA CRÍTICA QUE ESTÁ A CAUSAR O ERRO
router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse, summary="Página principal com as ofertas")
async def get_offers_page(
        request: Request,
        country: str = Query("PT", description="Código do país (PT, BR, US)")
):
    """
    Renderiza a página HTML que exibe as ofertas de um determinado país.
    """
    raw_offers = await hodlhodl_service.get_hodlhodl_offers(country_code=country, payment_method=None)
    processed_offers = hodlhodl_service.process_and_enrich_offers(raw_offers)
    offers = [Offer.parse_obj(o) for o in processed_offers]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "offers": offers,
        "selected_country": country,
    })

@router.get("/api/offers", response_model=List[Offer], summary="Endpoint de dados das ofertas")
async def api_get_offers(
        country_code: str = Query("PT", description="Código do país (PT, BR, US)"),
        payment_method: str = Query(None, description="Filtra por método de pagamento")
):
    """
    Endpoint da API que retorna uma lista de ofertas em formato JSON.
    """
    try:
        raw_offers = await hodlhodl_service.get_hodlhodl_offers(country_code, payment_method)
        processed_offers = hodlhodl_service.process_and_enrich_offers(raw_offers)
        # Filtra os dicionários que não puderam ser parseados para o schema Offer
        valid_offers = []
        for o in processed_offers:
            try:
                valid_offers.append(Offer.parse_obj(o))
            except Exception:
                continue # Ignora ofertas com dados inesperados
        return valid_offers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))