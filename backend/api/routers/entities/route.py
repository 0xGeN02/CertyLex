"""
Router para la extracción de entidades en documentos
"""
from fastapi import APIRouter, Body
from pydantic import BaseModel
import re
import sys
import os
from typing import List

# Aseguramos que la ruta de backend está en sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Ahora importamos los módulos necesarios
from backend.lib.language.regex import nif_detector, name_detector, nif_empresa_detector

# Creamos un router en lugar de una app completa
entity_router = APIRouter(
    prefix="/entities",
    tags=["Entities"],
)

class TextRequest(BaseModel):
    text: str

class ExtractionResponse(BaseModel):
    nombres: List[str]
    nifs: List[str] 
    nif_empresa: List[str]

@entity_router.post("/extract", response_model=ExtractionResponse)
async def extract_entities(request: TextRequest = Body(...)):
    """
    Extrae entidades (nombres, NIFs personales y NIFs de empresa) de un texto.
    
    Args:
        request: Objeto con el texto a analizar
        
    Returns:
        Objeto con las listas de entidades extraídas
    """
    text = request.text
    
    # Usar las funciones ya implementadas
    nombres = name_detector(text)
    nifs = nif_detector(text)
    nif_empresa = nif_empresa_detector(text)
    
    return ExtractionResponse(
        nombres=nombres,
        nifs=nifs,
        nif_empresa=nif_empresa
    )
