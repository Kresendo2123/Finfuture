from pydantic import BaseModel
from datetime import datetime


class CoinSchema(BaseModel):
    id: int
    name: str
    symbol: str

    class Config:
        from_attributes = True


class CoinPriceSchema(BaseModel):
    id: int
    coin_id: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime

    class Config:
        from_attributes = True


class CoinPredictionSchema(BaseModel):
    id: int
    coin_id: int
    predicted_price: float
    timestamp: datetime
    predict: int

    class Config:
        from_attributes = True
