# app/predict/ada_model.py

import pandas as pd
import numpy as np
import requests
import joblib
from tensorflow.keras.models import load_model
from datetime import datetime
import os
from app.db import get_db
from app.models import CoinPrediction


def compute_rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_ada_data():
    url = "https://api.binance.com/api/v3/klines?symbol=ADAUSDT&interval=1d&limit=100"
    df = pd.DataFrame(requests.get(url).json(), columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "_1", "_2", "_3", "_4", "_5", "_6"
    ])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)

    # Teknik göstergeler
    df['pct_change'] = df['close'].pct_change()
    df['ma_5'] = df['close'].rolling(window=5).mean()
    df['ma_10'] = df['close'].rolling(window=10).mean()
    df['rsi_14'] = compute_rsi(df['close'])
    df['close_open_ratio'] = df['close'] / df['open']
    df['high_low_ratio'] = df['high'] / df['low']

    df = df.dropna().reset_index(drop=True)
    return df

def predict_ada_next_day():
    df = get_ada_data()

    feature_cols = [
        'open', 'high', 'low', 'close',
        'pct_change', 'ma_5', 'ma_10',
        'rsi_14', 'close_open_ratio', 'high_low_ratio'
    ]

    if len(df) < 20:
        return {"error": "Yeterli veri yok"}

    X_latest = df[feature_cols].values[-10:]  # son 10 gün
    X_latest = X_latest.reshape((1, 10, len(feature_cols)))

    BASE_DIR = os.path.dirname(__file__)
    model_path = os.path.join(BASE_DIR, '../../models/lstm_gru_crypto_model.h5')
    scaler_path = os.path.join(BASE_DIR, '../../models/crypto_scaler.joblib')

    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    X_scaled = scaler.transform(X_latest.reshape(-1, len(feature_cols))).reshape(1, 10, len(feature_cols))

    y_pred = model.predict(X_scaled)[0][0]
    direction = int(y_pred > 0.5)
    last_close = df['close'].iloc[-1]

    db = next(get_db())
    prediction = CoinPrediction(
        coin_id=10,  # ADA'nın ID'si
        predicted_price=0,
        predict=direction,
        timestamp=datetime.utcnow()
    )
    db.add(prediction)
    db.commit()

if __name__ == "__main__":
    predict_ada_next_day()