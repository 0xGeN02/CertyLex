import { NextRequest, NextResponse } from 'next/server';

const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:5328';

export async function POST(request: NextRequest) {
  try {
    const { text } = await request.json();

    if (!text) {
      return NextResponse.json(
        { error: 'Se requiere el texto para el análisis' },
        { status: 400 }
      );
    }

    // Llamada al backend de Python para la extracción de entidades
    const extractionRes = await fetch(`${BACKEND_API_URL}/api/nlp_entities/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    if (!extractionRes.ok) {
      const errorText = await extractionRes.text();
      console.error("Error from Python API:", errorText);
      return NextResponse.json(
        { error: 'Error en la extracción de entidades', details: errorText },
        { status: extractionRes.status }
      );
    }

    const data = await extractionRes.json();
    
    // Retornar los resultados de la extracción
    return NextResponse.json({
      nombres: data.nombres,
      nifs: data.nifs,
      nif_empresa: data.nif_empresa
    });

  } catch (e) {
    console.error('Error durante la extracción de entidades:', e);
    return NextResponse.json(
      { error: 'Error interno del servidor' },
      { status: 500 }
    );
  }
}

export function GET() {
  return NextResponse.json({ message: 'Use POST para enviar texto a analizar' });
}
