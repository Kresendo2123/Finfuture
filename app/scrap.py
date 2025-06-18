import schedule
import time
import requests
from datetime import datetime
from db import get_db
from models import CoinPrice
import pytz
from app.log_config import logger  # 🔹 Log sistemi entegre

# 🔹 İzlenen coin listesi
coins = [
    {"id": 1, "symbol": "BTCUSDT"},
    {"id": 2, "symbol": "ETHUSDT"},
    {"id": 4, "symbol": "XRPUSDT"},
    {"id": 5, "symbol": "BNBUSDT"},
    {"id": 6, "symbol": "SOLUSDT"},
    {"id": 7, "symbol": "USDCUSDT"},
    {"id": 8, "symbol": "TRXUSDT"},
    {"id": 9, "symbol": "DOGEUSDT"},
    {"id": 10, "symbol": "ADAUSDT"},
]

turkey_tz = pytz.timezone('Europe/Istanbul')


# 🟢 Coin verilerini çekip veritabanına kaydet
def fetch_and_save_btc_data():
    session = next(get_db())

    for coin in coins:
        url = f"https://api.binance.com/api/v3/klines?symbol={coin['symbol']}&interval=1m&limit=1"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()[0]

                price = CoinPrice(
                    coin_id=coin["id"],
                    open=data[1],
                    high=data[2],
                    low=data[3],
                    close=data[4],
                    volume=data[5],
                    timestamp=datetime.fromtimestamp(data[0] / 1000, pytz.utc).astimezone(turkey_tz)
                )

                session.add(price)
                logger.info(f"[{coin['symbol']}] Fiyat verisi kaydedildi: close={price.close} - {price.timestamp}")
            else:
                logger.error(f"[{coin['symbol']}] API hatası: Status code {response.status_code}")
        except Exception as e:
            logger.exception(f"[{coin['symbol']}] İstek sırasında hata oluştu: {str(e)}")

    try:
        session.commit()
        logger.info("✅ Tüm coin verileri başarıyla veritabanına yazıldı.")
    except Exception as e:
        logger.error(f" Commit hatası: {str(e)}")
    finally:
        session.close()


# 🕒 Her dakika çalışacak şekilde zamanlayıcı kur
schedule.every(1).minutes.do(fetch_and_save_btc_data)

logger.info("⏱️ Zamanlayıcı başlatıldı. Çıkmak için Ctrl+C")

while True:
    schedule.run_pending()
    time.sleep(1)
