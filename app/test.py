from db import get_db

def test_connection():
    try:
        db = next(get_db())
        print("✅ Veritabanı bağlantısı başarılı!")
    except Exception as e:
        print(f"❌ Veritabanı bağlantısı HATA: {e}")

if __name__ == "__main__":
    test_connection()
