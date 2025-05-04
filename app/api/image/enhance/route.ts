import { NextRequest, NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import { join } from 'path';
import { v4 as uuidv4 } from 'uuid';
import os from 'os';

const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:5328';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const imageFile = formData.get('image') as File;
    
    if (!imageFile) {
      return NextResponse.json(
        { error: 'No se ha proporcionado una imagen' },
        { status: 400 }
      );
    }

    // Validar el tipo de archivo
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(imageFile.type)) {
      return NextResponse.json(
        { error: 'Tipo de archivo no válido. Solo se permiten JPG, PNG y WEBP' },
        { status: 400 }
      );
    }

    // Guardar la imagen temporalmente
    const bytes = await imageFile.arrayBuffer();
    const buffer = Buffer.from(bytes);
    
    // Crear un directorio temporal para almacenar la imagen
    const tempDir = os.tmpdir();
    const uniqueId = uuidv4();
    const tempFilePath = join(tempDir, `${uniqueId}_${imageFile.name}`);
    
    // Escribir el archivo al sistema
    await writeFile(tempFilePath, buffer);
    
    // Crear FormData para enviar al backend Python
    const backendFormData = new FormData();
    const backendImageFile = new File([buffer], imageFile.name, { type: imageFile.type });
    backendFormData.append('image', backendImageFile);
    
    // Enviar la imagen al backend para su procesamiento
    const enhanceResponse = await fetch(`${BACKEND_API_URL}/api/image/enhance`, {
      method: 'POST',
      body: backendFormData,
    });

    if (!enhanceResponse.ok) {
      const errorText = await enhanceResponse.text();
      console.error("Error from Python API:", errorText);
      return NextResponse.json(
        { error: 'Error al procesar la imagen', details: errorText },
        { status: enhanceResponse.status }
      );
    }

    // Obtener la respuesta del backend
    const data = await enhanceResponse.json();
    
    // Devolver los datos de la imagen procesada
    return NextResponse.json({
      originalImage: data.original_url || null,
      enhancedImage: data.enhanced_url || null,
      metadata: data.metadata || {},
      processingSteps: data.processing_steps || []
    });

  } catch (e) {
    console.error('Error durante el procesamiento de la imagen:', e);
    return NextResponse.json(
      { error: 'Error interno del servidor' },
      { status: 500 }
    );
  }
}

export function GET() {
  return NextResponse.json({ message: 'Use POST para enviar una imagen a procesar' });
}
