import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
from datetime import datetime
from app.scrap_for_ml import get_combined_data
from app.db import get_db
from app.models import CoinPrediction

BTC_FILE = '../../data/BTC.csv'
WTI_FILE = '../../data/Crude_Oil_WTI.csv'
NASDAQ_FILE = '../../data/NASDAQ.csv'
MODEL_FILE = '../../models/rf_model_gm_direction.pkl'

# --- Gri Model hesaplaması ---
def compute_gm_direction(btc_series, nasdaq_series, wti_series):
    x0 = btc_series.values
    x1 = nasdaq_series.values
    x2 = wti_series.values
    X = np.vstack([x0, x1, x2])
    X1 = np.cumsum(X, axis=1)
    Z = 0.5 * (X1[0, :-1] + X1[0, 1:]).reshape(1, -1)
    B = np.vstack([-Z, X1[1:, 1:]]).T
    Y = X[0, 1:].reshape(-1, 1)

    theta = np.linalg.inv(B.T @ B) @ B.T @ Y
    a = theta[0, 0]
    b = theta[1:, 0]

    x0_pred = [x0[0]]
    for k in range(1, len(x0)):
        term = sum(b[i] * (X1[i + 1, k - 1] - X1[i + 1, k - 2]) for i in range(len(b)))
        next_value = (x0[0] - term / a) * np.exp(-a * k) + term / a
        x0_pred.append(next_value)

    gm_dir = pd.Series(x0_pred).shift(-1) > pd.Series(x0_pred)
    return gm_dir.astype(int).fillna(0)

# --- Model eğitimi ---
def train_model():
    btc_df = pd.read_csv(BTC_FILE)
    wti_df = pd.read_csv(WTI_FILE)
    nasdaq_df = pd.read_csv(NASDAQ_FILE)

    btc_df['date'] = pd.to_datetime(btc_df['date'])
    wti_df['Date'] = pd.to_datetime(wti_df['Date'])
    nasdaq_df['Date'] = pd.to_datetime(nasdaq_df['Date'])

    btc_df = btc_df[['date', 'close']].rename(columns={'date': 'Date', 'close': 'BTC_Close'})
    wti_df = wti_df[['Date', 'Price']].rename(columns={'Price': 'WTI_Price'})
    nasdaq_df = nasdaq_df[['Date', 'Close/Last']].rename(columns={'Close/Last': 'NASDAQ_Close'})

    df = pd.merge(btc_df, wti_df, on='Date', how='inner')
    df = pd.merge(df, nasdaq_df, on='Date', how='inner')
    df = df.sort_values('Date').reset_index(drop=True)

    df['GM_Direction'] = compute_gm_direction(df['BTC_Close'], df['NASDAQ_Close'], df['WTI_Price'])
    df['Actual_Direction'] = (df['BTC_Close'].shift(-1) > df['BTC_Close']).astype(int)
    df = df.dropna()

    features = ['NASDAQ_Close', 'WTI_Price', 'GM_Direction']
    X = df[features]
    y = df['Actual_Direction']

    split_index = int(len(df) * 0.8)
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("Model Performansı:")
    print(classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_FILE)
    print("Model kaydedildi.")

# --- Tahmin + veritabanına yazım ---
def predict_next_day():
    df = get_combined_data()
    df['GM_Direction'] = compute_gm_direction(df['BTC_Close'], df['NASDAQ_Close'], df['WTI_Price'])
    features = ['NASDAQ_Close', 'WTI_Price', 'GM_Direction']
    X_latest = df[features].iloc[-1:].copy()

    model = joblib.load(MODEL_FILE)
    pred = model.predict(X_latest)[0]

    prediction_date = df["Date"].iloc[-1]
    print(f"[BTC] Tahmin edilen yön: {'Artış' if pred == 1 else 'Azalış'} - Tarih: {prediction_date}")

    # --- Veritabanına yaz ---
    db = next(get_db())
    prediction = CoinPrediction(
        coin_id=1,
        predicted_price=0,
        predict=int(pred),
        timestamp=datetime.combine(prediction_date, datetime.min.time())
    )
    db.add(prediction)
    db.commit()
    print("Tahmin veritabanına kaydedildi.")

# --- Ana giriş noktası ---
if __name__ == '__main__':
    #train_model()
    predict_next_day()
