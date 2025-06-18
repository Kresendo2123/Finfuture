from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models import Coin, CoinPrice, CoinPrediction
from db import get_db
from typing import List
from orm import CoinSchema, CoinPriceSchema, CoinPredictionSchema
from fastapi.middleware.cors import CORSMiddleware
from app.log_config import logger  # 🔹 log sistemi eklendi

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # güvenlik için gerekirse sadece Flutter IP'si gir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/coins", response_model=List[CoinSchema])
def get_coins(db: Session = Depends(get_db)):
    try:
        coins = db.query(Coin).all()
        logger.info("Tüm coin bilgileri başarıyla getirildi.")
        return coins
    except Exception as e:
        logger.error(f"/coins endpointinde hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prices/{coin_id}", response_model=List[CoinPriceSchema])
def get_prices_by_coin(
        coin_id: int,
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db)
):
    try:
        prices = (
            db.query(CoinPrice)
            .filter(CoinPrice.coin_id == coin_id)
            .order_by(CoinPrice.timestamp.desc())
            .limit(limit)
            .all()
        )
        logger.info(f"/prices/{coin_id} endpointi başarıyla çalıştı, {len(prices)} kayıt çekildi.")
        return list(reversed(prices))
    except Exception as e:
        logger.error(f"/prices/{coin_id} endpointinde hata: {e}")
        raise HTTPException(status_code=500, detail="Veri çekilemedi")


@app.get("/predictions/{coin_id}", response_model=List[CoinPredictionSchema])
def get_predictions(
        coin_id: int,
        limit: int = Query(10, ge=1, le=1000),
        db: Session = Depends(get_db)
):
    try:
        preds = (
            db.query(CoinPrediction)
            .filter(CoinPrediction.coin_id == coin_id)
            .order_by(CoinPrediction.timestamp.desc())
            .limit(limit)
            .all()
        )
        logger.info(f"/predictions/{coin_id} çağrıldı, {len(preds)} kayıt getirildi.")
        return list(reversed(preds))
    except Exception as e:
        logger.error(f"/predictions/{coin_id} endpointinde hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))
