from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import csv
import io
from datetime import datetime
from typing import List

import models, schemas
from database import engine, get_db

app = FastAPI(title="IoT Data API", version="1.0")

# Crea las tablas en la base de datos al iniciar
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# --- Endpoint para subir el archivo CSV ---
@app.post("/upload-csv/", response_model=List[schemas.SensorDataResponse], status_code=status.HTTP_201_CREATED)
async def upload_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    # 1. Validar que sea un archivo CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser de tipo CSV")

    # 2. Leer y parsear el contenido del archivo
    contents = await file.read()
    try:
        decoded_contents = contents.decode("utf-8")
        csv_reader = csv.DictReader(decoded_contents.splitlines())
        data_list = list(csv_reader)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al leer el archivo CSV: {str(e)}")

    if not data_list:
        raise HTTPException(status_code=400, detail="El archivo CSV está vacío")

    # 3. Validar y guardar cada fila en la base de datos
    sensor_data_instances = []
    for row in data_list:
        try:
            # Validamos que los campos requeridos existan
            if not all(k in row for k in ('device_id', 'distancia', 'aceleracion', 'humedad')):
                raise HTTPException(status_code=400, detail="Formato de CSV inválido. Columnas requeridas: device_id, distancia, aceleracion, humedad")

            # Creamos un objeto Pydantic para validar los tipos
            data_in = schemas.SensorDataCreate(
                device_id=row['device_id'],
                distancia=float(row['distancia']),
                aceleracion=float(row['aceleracion']),
                humedad=float(row['humedad']),
                timestamp=datetime.fromisoformat(row['timestamp']) if 'timestamp' in row and row['timestamp'] else None
            )
            # Creamos la instancia del modelo de SQLAlchemy
            db_data = models.SensorData(**data_in.model_dump(exclude_unset=True))
            sensor_data_instances.append(db_data)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Error de tipo de dato en el CSV: {str(e)}")

    # Agregamos todos a la sesión y hacemos commit
    db.add_all(sensor_data_instances)
    await db.commit()
    for instance in sensor_data_instances:
        await db.refresh(instance)

    # Devolvemos los datos creados
    return sensor_data_instances

# --- Endpoint de prueba (opcional) ---
@app.get("/")
async def root():
    return {"message": "API IoT funcionando correctamente"}
