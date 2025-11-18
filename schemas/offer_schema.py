from pydantic import BaseModel, Field

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

    class Config:
        # Permite que o Pydantic mapeie dados mesmo que não sejam um dicionário
        from_attributes = True