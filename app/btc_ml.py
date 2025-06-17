# --- Gri Tahmin Fonksiyonu (GM(1,N)) ---
import requests

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from scrap_for_ml import get_combined_data , get_ada_data
from tensorflow.keras.models import load_model

BTC_FILE = '../data/BTC.csv'
WTI_FILE = '../data/Crude_Oil_WTI.csv'
NASDAQ_FILE = '../data/NASDAQ.csv'
MODEL_FILE = '../models/rf_model_gm_direction.pkl'



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


# --- Model Eğitimi ---
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

    # --- Tahmin Fonksiyonu ---


def predict_next_day():
    df = get_combined_data()  # Günlük BTC, WTI, NASDAQ verileri geliyor

    # btc_df = pd.read_csv(BTC_FILE)
    # wti_df = pd.read_csv(WTI_FILE)
    # nasdaq_df = pd.read_csv(NASDAQ_FILE)
    #
    # btc_df['date'] = pd.to_datetime(btc_df['date'])
    # wti_df['Date'] = pd.to_datetime(wti_df['Date'])
    # nasdaq_df['Date'] = pd.to_datetime(nasdaq_df['Date'])
    #
    # btc_df = btc_df[['date', 'close']].rename(columns={'date': 'Date', 'close': 'BTC_Close'})
    # wti_df = wti_df[['Date', 'Price']].rename(columns={'Price': 'WTI_Price'})
    # # nasdaq_df = nasdaq_df[['Date', 'Close/Last']].rename(columns={'Close/Last': 'NASDAQ_Close'})
    #
    # df = pd.merge(btc_df, wti_df, on='Date', how='inner')
    # df = pd.merge(df, nasdaq_df, on='Date', how='inner')
    # df = df.sort_values('Date').reset_index(drop=True)

    df['GM_Direction'] = compute_gm_direction(df['BTC_Close'], df['NASDAQ_Close'], df['WTI_Price'])
    features = ['NASDAQ_Close', 'WTI_Price', 'GM_Direction']
    X_latest = df[features].iloc[-1:].copy()

    model = joblib.load(MODEL_FILE)
    pred = model.predict(X_latest)[0]
    #direction = 'Artış' if pred == 1 else 'Azalış'
    #print(f"Tahmin edilen yön ({df['Date'].iloc[-1].strftime('%Y-%m-%d')} sonrası): {direction}")
    payload = {
        "coin_id": 1,
        "predicted_price": 0,  # Gerçek tahminse burada kullan
        "timestamp": str(df["Date"].iloc[-1]),
        "predict": int(pred)  # 0 veya 1
    }

    res = requests.post("http://localhost:8000/predictions", json=payload)
    print(res.json())


def predict_ada_next_day():
    # 📥 1. Veriyi al
    df = get_ada_data()

    # 📊 2. Özellikleri aynı sırayla al
    feature_cols = [
        'open', 'high', 'low', 'close',
        'pct_change', 'ma_5', 'ma_10',
        'rsi_14', 'close_open_ratio', 'high_low_ratio'
    ]

    # ⛔ Yeterli veri kontrolü (örneğin 10 günlük pencere için min 20 satır mantıklı)
    if len(df) < 20:
        print("Yeterli veri yok")
        return

    X_latest = df[feature_cols].values[-10:]  # son 10 gün
    X_latest = X_latest.reshape((1, 10, len(feature_cols)))

    # 🧪 3. Model ve scaler yükle
    model = load_model("lstm_gru_crypto_model.h5")

    scaler = joblib.load("crypto_scaler.joblib")

    X_scaled = scaler.transform(X_latest.reshape(-1, len(feature_cols))).reshape(1, 10, len(feature_cols))

    # 🔮 4. Tahmin yap
    y_pred = model.predict(X_scaled)[0][0]
    direction = int(y_pred > 0.5)  # 1 = artış, 0 = azalış

    # 🧾 5. Son kapanış fiyatını da hesaplayabiliriz (tahmini değil ama referans)
    last_close = df['close'].iloc[-1]

    # 🗓️ 6. Tahmin günü
    prediction_date = df["date"].iloc[-1].date()
    print(f"Tahmin edilen yön: {'Artış' if direction == 1 else 'Azalış'}")
    print(f"Model çıktısı (olasılık): {y_pred:.4f}")
    # # 🌐 7. API'ye POST et
    # payload = {
    #     "coin_id": 10,  # ADA için
    #     "predicted_price": None,  # fiyat değil yön tahmini yaptık
    #     "timestamp": str(prediction_date),
    #     "predict": direction
    # }
    #
    # try:
    #     res = requests.post("http://localhost:8000/predictions", json=payload)
    #     print(f"Tahmin gönderildi: {res.status_code} - {res.json()}")
    # except Exception as e:
    #     print("Gönderim hatası:", str(e))




# if __name__ == '__main__':
#     # İlk kullanımda model eğitmek için uncomment et:
#     # train_model()
#     #train_model()
#
#     if __name__ == '__main__':
#         # İlk kullanımda model eğitmek için uncomment et:
#         # train_model()
#         predict_ada_next_day()
