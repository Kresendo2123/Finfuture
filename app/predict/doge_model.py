# app/predict/doge_model.py

import pandas as pd
import numpy as np
import joblib
import requests
from datetime import datetime
import os

from app.db import get_db
from app.models import CoinPrediction

# --- Dosya yolları ---
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, '../../models/doge_model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, '../../models/doge_scaler.pkl')

FEATURES = ['pct_change', 'volatility', 'sma_5', 'return_3', 'momentum_5', 'ema_10']

# --- DOGE verisini Binance'ten çek ---
def get_doge_data():
    url = "https://api.binance.com/api/v3/klines?symbol=DOGEUSDT&interval=1d&limit=100"
    df = pd.DataFrame(requests.get(url).json(), columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "_1", "_2", "_3", "_4", "_5", "_6"
    ])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    return df[["date", "open", "high", "low", "close"]]

# --- Özellik mühendisliği ---
def preprocess_doge(df):
    df = df.sort_values('date').reset_index(drop=True)
    df['pct_change'] = df['close'].pct_change()
    df['volatility'] = (df['high'] - df['low']) / df['open']
    df['sma_5'] = df['close'].rolling(window=5).mean()
    df['return_3'] = df['close'].pct_change(3)
    df['momentum_5'] = df['close'] - df['close'].shift(5)
    df['ema_10'] = df['close'].ewm(span=10).mean()
    df = df.dropna().reset_index(drop=True)
    return df

# --- Tahmin ve DB kaydı ---
def predict_doge_next_day():
    df = get_doge_data()
    df = preprocess_doge(df)

    if len(df) < 15:
        print("Yeterli veri yok.")
        return

    last_row = df[FEATURES].iloc[-1:]

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    X_input = scaler.transform(last_row)
    prediction = int(model.predict(X_input)[0])

    prediction_date = df["date"].iloc[-1].date()
    print(f"[DOGE] Tahmin edilen yön: {'Artış' if prediction == 1 else 'Azalış'} - Tarih: {prediction_date}")

    # DB'ye yaz
    db = next(get_db())
    prediction_record = CoinPrediction(
        coin_id=9,  # DOGE için ID
        predicted_price=0.0,
        predict=prediction,
        timestamp=datetime.combine(prediction_date, datetime.min.time())
    )
    db.add(prediction_record)
    db.commit()
    print("DOGE tahmini veritabanına kaydedildi.")

# --- Main ---
if __name__ == "__main__":
    predict_doge_next_day()
