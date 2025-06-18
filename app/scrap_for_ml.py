import pandas as pd
import requests
import yfinance as yf
from datetime import datetime
from app.log_config import logger  # 🔹 Log eklendi

# 🔹 1. BTC verisini Binance'ten çek
def get_btc_data():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=100"
        response = requests.get(url, timeout=10)
        data = response.json()

        btc_df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "_1", "_2", "_3", "_4", "_5", "_6"
        ])
        btc_df["Date"] = pd.to_datetime(btc_df["timestamp"], unit="ms").dt.date
        btc_df["BTC_Close"] = btc_df["close"].astype(float)

        logger.info("✅ BTC verisi başarıyla çekildi.")
        return btc_df[["Date", "BTC_Close"]]
    except Exception as e:
        logger.error(f"⛔ BTC verisi çekilemedi: {e}")
        return pd.DataFrame()

# 🔹 2. WTI verisini Yahoo Finance'ten çek
def get_wti_data():
    try:
        wti = yf.download("CL=F", period="100d", interval="1d", progress=False, auto_adjust=False)
        if isinstance(wti.columns, pd.MultiIndex):
            wti.columns = [col[0] for col in wti.columns]

        wti = wti.reset_index()
        wti["Date"] = pd.to_datetime(wti["Date"]).dt.date
        wti.rename(columns={"Close": "WTI_Price"}, inplace=True)

        logger.info("✅ WTI verisi başarıyla çekildi.")
        return wti[["Date", "WTI_Price"]]
    except Exception as e:
        logger.error(f"⛔ WTI verisi çekilemedi: {e}")
        return pd.DataFrame()

# 🔹 3. NASDAQ verisini Yahoo Finance'ten çek
def get_nasdaq_data():
    try:
        nasdaq = yf.download("^IXIC", period="100d", interval="1d", progress=False, auto_adjust=False)
        if isinstance(nasdaq.columns, pd.MultiIndex):
            nasdaq.columns = [col[0] for col in nasdaq.columns]

        nasdaq = nasdaq.reset_index()
        nasdaq["Date"] = pd.to_datetime(nasdaq["Date"]).dt.date
        nasdaq.rename(columns={"Close": "NASDAQ_Close"}, inplace=True)

        logger.info("✅ NASDAQ verisi başarıyla çekildi.")
        return nasdaq[["Date", "NASDAQ_Close"]]
    except Exception as e:
        logger.error(f"⛔ NASDAQ verisi çekilemedi: {e}")
        return pd.DataFrame()

# 🔹 4. Hepsini birleştir
def get_combined_data():
    btc_df = get_btc_data()
    wti_df = get_wti_data()
    nasdaq_df = get_nasdaq_data()

    if btc_df.empty or wti_df.empty or nasdaq_df.empty:
        logger.warning("⚠️ En az bir veri seti boş geldi. get_combined_data eksik olabilir.")

    try:
        df = pd.merge(btc_df, wti_df, on="Date", how="inner")
        df = pd.merge(df, nasdaq_df, on="Date", how="inner")
        logger.info("📊 Tüm veriler başarıyla birleştirildi.")
        return df
    except Exception as e:
        logger.error(f"⛔ Veri birleştirme hatası: {e}")
        return pd.DataFrame()
