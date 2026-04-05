from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SensorDataCreate(BaseModel):
    device_id: str
    distancia: float
    aceleracion: float
    humedad: float
    timestamp: Optional[datetime] = None  # Si no se envía, usaremos el actual

class SensorDataResponse(SensorDataCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
