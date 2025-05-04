"""
Main file for the FastAPI application
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Crear la aplicación FastAPI
app = FastAPI(
    title="CertyLex API",
    description="API para el análisis de documentos legales",
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Ajusta para tu entorno
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers
from backend.api.routers.entities.route import entity_router
from backend.api.routers.nlp_entities.route import nlp_entity_router

# Incluir routers en la aplicación
app.include_router(entity_router, prefix="/api")
app.include_router(nlp_entity_router, prefix="/api")

# Rutas básicas
API_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FAVICON_PATH = os.path.join(API_ROOT_DIR, "static/favicon.ico")

@app.get("/")
async def home():
    """
    Home page of the API
    """
    return {"message": "Hello, from CertyLex API!", "endpoints": ["/api/entities/extract"]}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Return the favicon
    """
    if not os.path.exists(FAVICON_PATH):
        raise HTTPException(status_code=404, detail="Favicon not found")
    return FileResponse(FAVICON_PATH)
