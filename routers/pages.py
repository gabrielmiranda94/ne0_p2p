from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse, summary="Nova Homepage (Manifesto)")
async def get_home_page(request: Request):
    """Renderiza a nova página principal (home.html)."""
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/offers", response_class=HTMLResponse, summary="Página de ofertas P2P")
async def get_offers_page(request: Request):
    """Renderiza a página de listagem de ofertas P2P (offers.html)."""
    return templates.TemplateResponse("offers.html", {"request": request})

@router.get("/wallets", response_class=HTMLResponse, summary="Página sobre carteiras de hardware")
async def get_wallets_page(request: Request):
    """Renderiza a página informativa sobre carteiras de hardware."""
    return templates.TemplateResponse("wallets.html", {"request": request})