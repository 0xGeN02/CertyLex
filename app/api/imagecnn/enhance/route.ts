import { NextRequest, NextResponse } from 'next/server';

const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:5328';

export async function POST(request: NextRequest) {
  try {
    // Reenviar la solicitud al backend de Python
    const formData = await request.formData();
    
    // Crear FormData para enviar al backend
    const response = await fetch(`${BACKEND_API_URL}/api/imagecnn/enhance`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Error from Python API:", errorText);
      return NextResponse.json(
        { error: 'Error en la API backend', details: errorText },
        { status: response.status }
      );
    }

    // Obtener la respuesta del backend y devolverla al cliente
    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (e) {
    console.error('Error durante el procesamiento de la imagen CNN:', e);
    return NextResponse.json(
      { error: 'Error interno del servidor' },
      { status: 500 }
    );
  }
}

export function GET() {
  return NextResponse.json({ message: 'Use POST para enviar una imagen a procesar con CNN' });
}
