import datetime  # 1. Importar a biblioteca datetime
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List

from schemas.offer_schema import Offer
from services import hodlhodl_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ... (a sua função _parse_offers_safely fica aqui, sem alterações) ...
def _parse_offers_safely(offers_data: List[dict]) -> List[Offer]:
    valid_offers = []
    for offer_dict in offers_data:
        try:
            valid_offers.append(Offer.parse_obj(offer_dict))
        except Exception:
            continue
    return valid_offers


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
    offers = _parse_offers_safely(processed_offers)

    # 2. Adicionar o ano atual ao contexto que vai para o template
    return templates.TemplateResponse("index.html", {
        "request": request,
        "offers": offers,
        "selected_country": country,
        "current_year": datetime.datetime.now().year  # AQUI ESTÁ A MUDANÇA
    })

# ... (a sua função api_get_offers fica aqui, sem alterações) ...
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
        offers = _parse_offers_safely(processed_offers)
        return offers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))