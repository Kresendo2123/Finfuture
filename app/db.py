from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

DATABASE_URL = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

# Veritabanı bağlantısını kurma
engine = create_engine(DATABASE_URL, echo=False)  # echo=True ile SQL sorguları loglanır

# Oturum üreticisi
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Veritabanı şemalarını oluşturma
Base.metadata.create_all(bind=engine)  # Tabloları oluşturmak için

# Veritabanı oturumlarını yöneten bir işlev
def get_db():
    db = SessionLocal()  # Yeni bir oturum başlat
    try:
        yield db
    finally:
        db.close()  # Oturum kapatıldığında bağlantıyı kapat
