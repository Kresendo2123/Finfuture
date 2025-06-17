from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

# Coin Modeli
class Coin(Base):
    __tablename__ = 'coins'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    symbol = Column(String, unique=True, nullable=False)

    prices = relationship("CoinPrice", back_populates="coin", cascade="all, delete-orphan")
    predictions = relationship("CoinPrediction", back_populates="coin", cascade="all, delete-orphan")
    errors = relationship("ModelError", back_populates="coin", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Coin(id={self.id}, name={self.name}, symbol={self.symbol})>"

# CoinPrice Modeli
class CoinPrice(Base):
    __tablename__ = 'coin_prices'

    id = Column(Integer, primary_key=True)
    coin_id = Column(Integer, ForeignKey('coins.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

    coin = relationship("Coin", back_populates="prices")

    def __repr__(self):
        return f"<CoinPrice(id={self.id}, coin_id={self.coin_id}, timestamp={self.timestamp}, open={self.open}, close={self.close})>"

# CoinPrediction Modeli
class CoinPrediction(Base):
    __tablename__ = 'coin_predictions'

    id = Column(Integer, primary_key=True)
    coin_id = Column(Integer, ForeignKey('coins.id'), nullable=False)
    predicted_price = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    predict = Column(Integer, nullable=False)
    coin = relationship("Coin", back_populates="predictions")

    def __repr__(self):
        return f"<CoinPrediction(id={self.id}, coin_id={self.coin_id}, predicted_price={self.predicted_price}, timestamp={self.timestamp})>"

# ModelError Modeli
class ModelError(Base):
    __tablename__ = 'model_errors'

    id = Column(Integer, primary_key=True)
    coin_id = Column(Integer, ForeignKey('coins.id'), nullable=False)
    error_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    coin = relationship("Coin", back_populates="errors")

    def __repr__(self):
        return f"<ModelError(id={self.id}, coin_id={self.coin_id}, error_value={self.error_value}, timestamp={self.timestamp})>"
