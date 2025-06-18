import pandas as pd
import numpy as np
import joblib
import requests
from datetime import datetime
import os

from app.db import get_db
from app.models import CoinPrediction
from app.log_config import logger  # 🔹 Log modülü eklendi

# Model yolları
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, '../../models/eth_model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, '../../models/eth_scaler.pkl')

FEATURES = ['pct_change', 'volatility', 'sma_5', 'return_3', 'momentum_5', 'ema_10']

# --- ETH verisini Binance'ten çek ---
def get_eth_data():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=1d&limit=100"
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
    except Exception as e:
        logger.error(f"[ETH] Veri çekme hatası: {str(e)}")
        return pd.DataFrame()

# --- Özellik çıkarımı ---
def preprocess_eth_data(df):
    try:
        df = df.sort_values('date').reset_index(drop=True)
        df['pct_change'] = df['close'].pct_change()
        df['volatility'] = (df['high'] - df['low']) / df['open']
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['return_3'] = df['close'].pct_change(3)
        df['momentum_5'] = df['close'] - df['close'].shift(5)
        df['ema_10'] = df['close'].ewm(span=10).mean()
        df = df.dropna().reset_index(drop=True)
        return df
    except Exception as e:
        logger.error(f"[ETH] Özellik çıkarma hatası: {str(e)}")
        return pd.DataFrame()

# --- Tahmin ve DB kaydı ---
def predict_eth_next_day():
    try:
        df = get_eth_data()
        df = preprocess_eth_data(df)

        if df.empty or len(df) < 20:
            logger.warning("[ETH] Yeterli veri yok, tahmin yapılmadı.")
            return

        X_input = df[FEATURES].iloc[-1:]

        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)

        X_scaled = scaler.transform(X_input)
        prediction = int(model.predict(X_scaled)[0])

        prediction_date = df["date"].iloc[-1].date()
        logger.info(f"[ETH] Tahmin edilen yön: {'Artış' if prediction == 1 else 'Azalış'} - Tarih: {prediction_date}")

        db = next(get_db())
        prediction_record = CoinPrediction(
            coin_id=2,
            predicted_price=0,
            predict=prediction,
            timestamp=datetime.combine(prediction_date, datetime.min.time())
        )
        db.add(prediction_record)
        db.commit()
        logger.info("[ETH] Tahmin veritabanına kaydedildi.")
    except Exception as e:
        logger.error(f"[ETH] Tahmin sırasında hata: {str(e)}")

# --- Main ---
if __name__ == "__main__":
    predict_eth_next_day()
