from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import offers

app = FastAPI(
    title="ne0_p2p - Agregador de Ofertas",
    description="Uma plataforma para encontrar as melhores ofertas P2P da Hodl Hodl.",
    version="1.0.0",
)

# Monta a pasta 'static' para servir ficheiros como CSS e JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclui as rotas definidas no ficheiro de ofertas
app.include_router(offers.router)