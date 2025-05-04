"""
Router para el procesamiento y mejora de imágenes usando CNN y metaheurísticas
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import os
import sys
import tempfile
import shutil
from typing import List, Dict, Any
from datetime import datetime

# Aseguramos que la ruta de backend está en sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Importamos el procesamiento de imágenes con CNN y metaheurísticas
from backend.lib.image.cnn_metaheuristic import process_image_cnn_metaheuristic

# Crear el router para las imágenes con CNN
imagecnn_router = APIRouter(
    prefix="/imagecnn",
    tags=["imagecnn"],
    responses={404: {"description": "Not found"}},
)

# Directorio para guardar imágenes procesadas (crear si no existe)
PROCESSED_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "processed_images")
os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)

@imagecnn_router.post("/enhance")
async def enhance_image_cnn(
    image: UploadFile = File(...),
    scale_factor: float = Form(2.0),
    optimization_iterations: int = Form(5)
):
    """
    Mejora la resolución y calidad de una imagen utilizando técnicas avanzadas
    basadas en CNN simulada y algoritmos metaheurísticos.
    
    Args:
        image: Archivo de imagen subido
        scale_factor: Factor de escala para aumentar la resolución
        optimization_iterations: Número de iteraciones para la optimización
    
    Returns:
        JSONResponse con URLs de las imágenes original y procesada, metadatos y pasos de procesamiento
    """
    # Verificar el tipo de archivo
    valid_types = ["image/jpeg", "image/png", "image/webp"]
    if image.content_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail="Tipo de archivo no válido. Solo se permiten JPG, PNG y WEBP"
        )
    
    try:
        # Guardar archivo temporalmente
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, image.filename)
        
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Verificar que la imagen puede ser leída
        img = cv2.imread(temp_file)
        if img is None:
            raise HTTPException(status_code=400, detail="No se pudo leer la imagen")
        
        # Procesar la imagen con el enfoque avanzado
        result = process_image_cnn_metaheuristic(
            temp_file, 
            scale_factor=scale_factor, 
            iterations=optimization_iterations
        )
        
        # Guardar imágenes procesadas
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = f"original_cnn_{timestamp}_{image.filename}"
        enhanced_filename = f"enhanced_cnn_{timestamp}_{image.filename}"
        
        original_path = os.path.join(PROCESSED_IMAGES_DIR, original_filename)
        enhanced_path = os.path.join(PROCESSED_IMAGES_DIR, enhanced_filename)
        
        cv2.imwrite(original_path, result["original"])
        cv2.imwrite(enhanced_path, result["processed"])
        
        # Construir URLs para acceder a las imágenes
        base_url = "/static/processed_images"
        original_url = f"{base_url}/{original_filename}"
        enhanced_url = f"{base_url}/{enhanced_filename}"
        
        # Limpiar archivos temporales
        shutil.rmtree(temp_dir)
        
        # Devolver respuesta con URLs y metadatos
        return JSONResponse({
            "original_url": original_url,
            "enhanced_url": enhanced_url,
            "metadata": result["metadata"],
            "processing_steps": result["history"],
            "method": "CNN simulada con optimización metaheurística"
        })
        
    except Exception as e:
        # Asegurar limpieza en caso de error
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")
