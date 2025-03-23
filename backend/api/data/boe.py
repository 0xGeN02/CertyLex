"""
API para obtener el sumario del BOE en formato JSON
"""

from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from backend.lib.api.boe import download_boe_sumario

app = FastAPI()

@app.get("/boe/{fecha}")
async def get_boe_sumario(fecha: str):
    """
    Endpoint para obtener el sumario del BOE en formato JSON para una fecha específica.
    """
    # Validar el formato de la fecha
    try:
        datetime.strptime(fecha, "%Y%m%d")  # Formato esperado: AAAAMMDD
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use AAAAMMDD.") from exc

    try:
        # Llamar a la función para descargar el sumario
        download_boe_sumario(fecha)
        return {"message": f"Sumario del BOE para la fecha {fecha} descargado correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {e}") from e

@app.get("/boe/{start_date}::{end_date}")
async def get_boe_sumario_range(start_date: str, end_date: str):
    """
    Endpoint para obtener el sumario del BOE en formato JSON para un rango de fechas.
    """
    # Validar el formato de las fechas
    try:
        datetime.strptime(start_date, "%Y%m%d")  # Formato esperado: AAAAMMDD
        datetime.strptime(end_date, "%Y%m%d")  # Formato esperado: AAAAMMDD
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use AAAAMMDD.") from exc

    try:
        # Convertir las fechas a objetos datetime
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")

        # Iterar sobre el rango de fechas
        current = start
        while current <= end:
            fecha = current.strftime("%Y%m%d")
            download_boe_sumario(fecha)
            current += timedelta(days=1)

        return {"message": "Sumarios del BOE para el rango de fechas descargados correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {e}") from e
