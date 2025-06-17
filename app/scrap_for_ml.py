import pandas as pd
import requests
import yfinance as yf
from datetime import datetime


# 🔹 1. BTC verisini Binance'ten çek (günlük)
def get_btc_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=100"
    response = requests.get(url)
    data = response.json()

    btc_df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "_1", "_2", "_3", "_4", "_5", "_6"
    ])
    btc_df["Date"] = pd.to_datetime(btc_df["timestamp"], unit="ms").dt.date
    btc_df["BTC_Close"] = btc_df["close"].astype(float)
    return btc_df[["Date", "BTC_Close"]]


# 🔹 2. WTI verisini Yahoo Finance'ten çek (simge: CL=F)
def get_wti_data():
    wti = yf.download("CL=F", period="100d", interval="1d", progress=False, auto_adjust=False)
    if isinstance(wti.columns, pd.MultiIndex):
        wti.columns = [col[0] for col in wti.columns]  # sadece ana isimleri al

    wti = wti.reset_index()
    wti["Date"] = pd.to_datetime(wti["Date"]).dt.date
    wti.rename(columns={"Close": "WTI_Price"}, inplace=True)

    return wti[["Date", "WTI_Price"]]


# 🔹 3. NASDAQ verisini Yahoo Finance'ten çek (simge: ^IXIC)
def get_nasdaq_data():
    nasdaq = yf.download("^IXIC", period="100d", interval="1d", progress=False, auto_adjust=False)
    if isinstance(nasdaq.columns, pd.MultiIndex):
        nasdaq.columns = [col[0] for col in nasdaq.columns]  # düzleştir

    nasdaq = nasdaq.reset_index()
    nasdaq["Date"] = pd.to_datetime(nasdaq["Date"]).dt.date
    nasdaq.rename(columns={"Close": "NASDAQ_Close"}, inplace=True)

    return nasdaq[["Date", "NASDAQ_Close"]]


# 🔹 4. Hepsini birleştir
def get_combined_data():
    btc_df = get_btc_data()
    wti_df = get_wti_data()
    nasdaq_df = get_nasdaq_data()

    df = pd.merge(btc_df, wti_df, on="Date", how="inner")
    df = pd.merge(df, nasdaq_df, on="Date", how="inner")
    return df


def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
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

    # Gereksizleri at
    df = df.dropna().reset_index(drop=True)

    return df


#if __name__ == "__main__":
    #     df = get_combined_data()
    #     print(df.tail())
