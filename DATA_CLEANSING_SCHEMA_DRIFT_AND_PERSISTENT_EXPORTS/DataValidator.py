from pydantic import BaseModel, Field


class MarketRecord(BaseModel):
    symbol: str = Field(min_length=1)
    price: float
    change_percent: float