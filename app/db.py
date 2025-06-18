from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from dotenv import load_dotenv
import os
from app.log_config import logger  # 🔹 log modülü eklendi

load_dotenv()

db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

if not all([db_user, db_pass, db_host, db_port, db_name]):
    logger.warning("Veritabanı bağlantısı için .env dosyasında eksik değişken var.")

DATABASE_URL = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

try:
    engine = create_engine(DATABASE_URL, echo=False)
    logger.info("Veritabanı bağlantısı başarıyla oluşturuldu.")
except Exception as e:
    logger.error(f"Veritabanı bağlantısı oluşturulamadı: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

try:
    Base.metadata.create_all(bind=engine)
    logger.info("Veritabanı tabloları oluşturuldu (veya zaten mevcut).")
except Exception as e:
    logger.error(f"Veritabanı tabloları oluşturulurken hata oluştu: {e}")
    raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("Veritabanı oturumu kapatıldı.")
