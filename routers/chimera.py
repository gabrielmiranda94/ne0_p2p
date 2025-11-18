from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/buy-chimera-no-kyc", response_class=HTMLResponse, summary="Página de compra direta Chimera")
async def get_chimera_page(request: Request):
    """Renderiza a página com o widget de compra direta Chimera."""
    return templates.TemplateResponse("chimera.html", {"request": request})