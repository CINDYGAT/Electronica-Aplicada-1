from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from database import Base

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)  # Identificador de tu ESP32
    distancia = Column(Float)
    aceleracion = Column(Float)
    humedad = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
