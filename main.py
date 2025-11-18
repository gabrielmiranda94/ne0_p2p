from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import offers, pages, chimera  # Importamos os três routers

app = FastAPI(
    title="ne0_p2p API",
    description="API para servir ofertas P2P e páginas do frontend.",
    version="1.0.0"
)

# Monta a pasta 'static' para servir CSS, JS, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclui os routers na aplicação
app.include_router(pages.router)
app.include_router(offers.router)
app.include_router(chimera.router) # Novo router adicionado