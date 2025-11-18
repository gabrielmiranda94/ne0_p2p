from pydantic import BaseModel, Field
from typing import Optional

class Offer(BaseModel):
    id: str
    asset_code: str
    side: str
    title: str = Field(..., alias="description")
    price: str
    min_amount: str
    max_amount: str
    country: str
    payment_method: str = Field(..., alias="payment_method_name")
    trader_username: str
    trader_rating: float
    affiliate_link: str

    # NOVOS CAMPOS PARA O COMPARADOR DE PREÇOS
    # Usamos 'Optional' porque se a API da CoinGecko falhar,
    # estes campos podem não existir.
    market_price: Optional[float] = None
    premium: Optional[float] = None

    class Config:
        from_attributes = True