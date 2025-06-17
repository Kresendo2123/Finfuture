import schedule
import time
import requests
from datetime import datetime
from db import get_db
from models import CoinPrice
import pytz

coins = [
    {"id": 1, "symbol": "BTCUSDT"},
    {"id": 2, "symbol": "ETHUSDT"},
    #{"id": 3, "symbol": "USDTUSD"},
    {"id": 4, "symbol": "XRPUSDT"},
    {"id": 5, "symbol": "BNBUSDT"},
    {"id": 6, "symbol": "SOLUSDT"},
    {"id": 7, "symbol": "USDCUSDT"},
    {"id": 8, "symbol": "TRXUSDT"},
    {"id": 9, "symbol": "DOGEUSDT"},
    {"id": 10, "symbol": "ADAUSDT"},
]
turkey_tz = pytz.timezone('Europe/Istanbul')


# 🟢 BTC verisi çekme ve veritabanına yazma
def fetch_and_save_btc_data():
    # Veritabanı oturumunu al
    session = next(get_db())  # get_db fonksiyonu ile oturum alınıyor
    #url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=1"
    for coin in coins:
        url = f"https://api.binance.com/api/v3/klines?symbol={coin['symbol']}&interval=1m&limit=1"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()[0]

            # CoinPrice nesnesi oluşturuluyor
            price = CoinPrice(
                coin_id=coin["id"],
                open=data[1],
                high=data[2],
                low=data[3],
                close=data[4],
                volume=data[5],
                timestamp=datetime.fromtimestamp(data[0] / 1000, pytz.utc).astimezone(turkey_tz)
            )

            # Veritabanına kaydetme
            #print(f"{price.timestamp} - Veri kaydedildi: close = {price.close}")
            session.add(price)

        else:
            print("Veri alınamadı.")
    session.commit()
    session.close()


# 🕒 Her 1 dakikada bir çalıştır
schedule.every(1).minutes.do(fetch_and_save_btc_data)

print("Zamanlayıcı başlatıldı. Çıkmak için Ctrl+C")

while True:
    schedule.run_pending()
    time.sleep(1)
