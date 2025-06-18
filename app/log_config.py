import logging
import os

# 🔸 logs klasörü yoksa oluştur
os.makedirs("logs", exist_ok=True)

# 🔸 Logger'ı ayarla
logging.basicConfig(
    filename='logs/system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 🔸 Modüller için kolay kullanım
logger = logging.getLogger("finfuture")
