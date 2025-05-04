"""
Router para el procesamiento y mejora de imágenes
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
import base64
from datetime import datetime

# Aseguramos que la ruta de backend está en sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Importamos las funciones de procesamiento de imágenes
from backend.lib.image.pipeline import (
    process_image, 
    resize_image,
    normalize_image,
    adjust_brightness_contrast,
    auto_crop,
    correct_image_rotation
)

from backend.lib.image.llm_pipeline import (
    build_pipeline,
    process_image as llm_process_image,
    evaluate_image_quality
)

# Crear el router para las imágenes
image_router = APIRouter(
    prefix="/image",
    tags=["image"],
    responses={404: {"description": "Not found"}},
)

# Directorio para guardar imágenes procesadas (crear si no existe)
PROCESSED_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "processed_images")
os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)

@image_router.post("/enhance")
async def enhance_image(
    image: UploadFile = File(...),
    scale_factor: float = Form(1.5),
    enhance_contrast: bool = Form(True),
    sharpen: bool = Form(True),
    auto_crop_enabled: bool = Form(True)
):
    """
    Mejora la resolución y calidad de una imagen.
    
    Args:
        image: Archivo de imagen subido
        scale_factor: Factor de escala para aumentar la resolución
        enhance_contrast: Si se debe mejorar el contraste
        sharpen: Si se debe aplicar un filtro de nitidez
        auto_crop_enabled: Si se debe recortar automáticamente la imagen
    
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
        
        # Leer imagen con OpenCV
        img = cv2.imread(temp_file)
        if img is None:
            raise HTTPException(status_code=400, detail="No se pudo leer la imagen")
        
        # Preparar pasos de procesamiento según parámetros recibidos
        processing_steps = []
        
        # Paso 1: Corregir rotación
        processing_steps.append(correct_image_rotation)
        
        # Paso 2: Mejorar contraste si está activado
        if enhance_contrast:
            processing_steps.append(lambda img: adjust_brightness_contrast(img, alpha=1.2, beta=10))
            
        # Paso 3: Recortar automáticamente si está activado
        if auto_crop_enabled:
            processing_steps.append(auto_crop)
        
        # Paso 4: Normalizar imagen
        processing_steps.append(normalize_image)
        
        # Paso 5: Aplicar filtro de nitidez si está activado
        if sharpen:
            processing_steps.append(lambda img: cv2.filter2D(img, -1, np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])))
        
        # Paso 6: Escalar imagen según factor
        processing_steps.append(lambda img: cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC))
        
        # Procesar la imagen con los pasos definidos
        result = process_image(temp_file, steps=processing_steps)
        
        # Guardar imágenes procesadas
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = f"original_{timestamp}_{image.filename}"
        enhanced_filename = f"enhanced_{timestamp}_{image.filename}"
        
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
            "metadata": {
                "original_size": result["metadata"].get("original_size", []),
                "processed_size": result["metadata"].get("processed_size", []),
                "scale_factor": scale_factor,
                "enhance_contrast": enhance_contrast,
                "sharpen": sharpen,
                "auto_crop": auto_crop_enabled
            },
            "processing_steps": result["history"]
        })
        
    except Exception as e:
        # Asegurar limpieza en caso de error
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")
