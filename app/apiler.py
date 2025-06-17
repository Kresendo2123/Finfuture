from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models import Coin, CoinPrice, CoinPrediction
from db import get_db
from typing import List
from orm import CoinSchema, CoinPriceSchema, CoinPredictionSchema
from fastapi.middleware.cors import CORSMiddleware


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
        return coins
    except Exception as e:
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

        return list(reversed(prices))
    except:
        raise HTTPException(status_code=500, detail="Veri çekilemedi")


@app.post("/predictions")
def add_prediction(pred: CoinPredictionSchema, db: Session = Depends(get_db)):
    try:
        prediction = CoinPrediction(**pred.dict())
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return {"status": "ok", "id": prediction.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        return list(reversed(preds))  # eski → yeni sıralı
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
