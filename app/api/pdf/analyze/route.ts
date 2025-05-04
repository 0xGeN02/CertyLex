import { NextResponse } from 'next/server';
import modelfile from '@/src/modelfile';

const OLLAMA_BASE_URL = process.env.OLLAMA_HOST || 'http://localhost:11434';

export async function POST(request: Request) {
  try {
    const { pdfContent, question, temperature = 0.5, top_p = 0.9, max_tokens = 2048 } = await request.json();

    if (!pdfContent) {
      return NextResponse.json(
        { error: 'Se requiere el contenido del PDF' },
        { status: 400 }
      );
    }

    // Preparamos un prompt específico para el análisis de documentos legales
    // que incluye el contenido del PDF y la pregunta del usuario
    const formattedQuestion = question || "Analiza este documento legal y proporciona mejoras";
    
    // Aplicamos el formato del modelfile para el input
    const prompt = `${modelfile.input.format.question.replace('{{user_input}}', formattedQuestion)}

DOCUMENTO A ANALIZAR:
${pdfContent}`;

    // Llamada a la API de Ollama
    const res = await fetch(
      `${OLLAMA_BASE_URL}/api/generate`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          model: 'llama3.2:3b', // Puedes ajustar esto para usar tu modelo específico
          prompt,
          stream: false,
          options: {
            temperature,
            top_p,
            num_predict: max_tokens
          }
        }),
      }
    );

    if (!res.ok) {
      const errorText = await res.text();
      console.error("Error from Ollama API:", errorText);
      return NextResponse.json(
        { error: 'Ollama request failed', details: errorText },
        { status: res.status }
      );
    }

    const data = await res.json();
    const aiResponse = data.response;

    // Procesamos la respuesta para extraer las diferentes partes según el formato del modelfile
    const processedResponse = processResponse(aiResponse);
    
    // Generamos una versión "mejorada" del documento
    const improvedDocument = generateImprovedDocument(pdfContent, processedResponse);

    // Retornamos tanto la respuesta formateada como el documento mejorado
    return NextResponse.json({
      formattedResponse: processedResponse.fullResponse,
      improvedDocument: improvedDocument
    });

  } catch (e) {
    console.error('Error durante el análisis de PDF:', e);
    return NextResponse.json(
      { error: 'Error interno del servidor' },
      { status: 500 }
    );
  }
}

// Función para procesar la respuesta del modelo según el formato esperado
function processResponse(response: string) {
  // Extraemos los componentes según el formato del modelfile
  const titleMatch = response.match(/Título:\s*(.*?)(?=\n\n|$)/s);
  const introMatch = response.match(/Introducción:\s*(.*?)(?=\n\n|$)/s);
  const detailsMatch = response.match(/Detalles:\s*(.*?)(?=\n\n|$)/s);
  const conclusionMatch = response.match(/Conclusión:\s*(.*?)(?=\n\n|$)/s);

  const title = titleMatch ? titleMatch[1].trim() : 'Análisis de Documento';
  const introduction = introMatch ? introMatch[1].trim() : '';
  const details = detailsMatch ? detailsMatch[1].trim() : '';
  const conclusion = conclusionMatch ? conclusionMatch[1].trim() : '';

  // Construimos la respuesta formateada completa
  const fullResponse = `
# ${title}

## Introducción
${introduction}

## Detalles
${details}

## Conclusión
${conclusion}
`;

  return {
    title,
    introduction,
    details,
    conclusion,
    fullResponse
  };
}

// Función para generar una versión "mejorada" del documento original
function generateImprovedDocument(originalContent: string, analysis: any) {
  // En una implementación real, se podrían aplicar modificaciones específicas 
  // basadas en el análisis. Por ahora, añadimos comentarios con las sugerencias.
  
  const lines = originalContent.split('\n');
  let improvedDocument = '';
  let currentSection = '';

  // Identificamos secciones comunes en documentos legales
  const sections = [
    { name: 'REUNIDOS', detected: false },
    { name: 'EXPONEN', detected: false },
    { name: 'CLÁUSULAS', detected: false },
    { name: 'PRIMERA', detected: false },
    { name: 'RESOLUCIÓN', detected: false },
    { name: 'LEY APLICABLE', detected: false }
  ];

  // Procesamos el documento línea por línea
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // Detectamos en qué sección estamos
    for (const section of sections) {
      if (line.includes(section.name)) {
        currentSection = section.name;
        section.detected = true;
        break;
      }
    }

    // Añadimos la línea original
    improvedDocument += line + '\n';
    
    // Añadimos sugerencias en puntos específicos
    if (currentSection === 'CLÁUSULAS' && line.includes('CLÁUSULAS') && !lines[i-1].includes('SUGERENCIAS')) {
      improvedDocument += '\n/* SUGERENCIAS DE MEJORA:\n';
      improvedDocument += `${analysis.introduction}\n*/\n\n`;
    }
    else if (currentSection === 'RESOLUCIÓN' && line.includes('RESOLUCIÓN') && !lines[i-1].includes('ALERTA')) {
      improvedDocument += '\n/* ALERTA - POSIBLE CLÁUSULA ABUSIVA:\n';
      improvedDocument += 'Esta cláusula podría considerarse abusiva al no permitir la resolución del contrato por ninguna de las partes.\n';
      improvedDocument += 'Se recomienda modificarla para incluir causas justificadas de resolución y preaviso razonable.\n*/\n\n';
    }
    else if (currentSection === 'LEY APLICABLE' && line.includes('arbitraje') && !lines[i+1].includes('NOTA')) {
      improvedDocument += '\n/* NOTA LEGAL:\n';
      improvedDocument += 'Se recomienda especificar la corte de arbitraje y el procedimiento a seguir.\n*/\n\n';
    }
  }

  // Añadimos un resumen de mejoras al final
  improvedDocument += '\n\n/* RESUMEN DE MEJORAS SUGERIDAS:\n';
  improvedDocument += `${analysis.conclusion}\n*/\n`;

  return improvedDocument;
}

export function GET() {
  return NextResponse.json({ message: 'Use POST to analyze a PDF' });
}
