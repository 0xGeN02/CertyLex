import { NextResponse } from 'next/server';

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
    
    // Aplicamos un formato estructurado para obtener mejores respuestas
    const prompt = `Eres un asistente legal especializado en análisis de documentos jurídicos. 
Analiza el siguiente documento legal y proporciona un análisis detallado con el siguiente formato EXACTO:

# Análisis del [Tipo de documento]

## Introducción
[Proporciona un resumen conciso del documento, su propósito y las partes involucradas]

## Detalles
[Analiza las cláusulas más importantes, identificando:
1. Cláusulas principales y su significado
2. Obligaciones de cada parte
3. Plazos relevantes
4. Condiciones económicas
5. Posibles cláusulas problemáticas o ambiguas]

## Conclusión
[Resume los puntos principales del documento, proporciona recomendaciones concretas y destaca los aspectos que requieren atención]

La pregunta específica del usuario es: "${formattedQuestion}"

DOCUMENTO A ANALIZAR:
${pdfContent}`;

    // Creamos también un prompt específico para obtener un resumen con sugerencias
    const summaryPrompt = `Eres un asistente legal especializado en documentos jurídicos.
Lee detenidamente el siguiente documento legal y proporciona:
1. Un resumen BREVE del contenido (máximo 3 párrafos)
2. Una lista de 5 sugerencias específicas y prácticas para mejorar este documento
3. Destaca los puntos más problemáticos que deberían corregirse inmediatamente

Formato tu respuesta así:

## RESUMEN
[Tu resumen aquí]

## SUGERENCIAS DE MEJORA
1. [Primera sugerencia]
2. [Segunda sugerencia]
3. [Tercera sugerencia]
4. [Cuarta sugerencia]
5. [Quinta sugerencia]

## PUNTOS CRÍTICOS
- [Primer punto crítico]
- [Segundo punto crítico]
- [Tercer punto crítico]

DOCUMENTO A ANALIZAR:
${pdfContent}`;

    // Llamada a la API de Ollama para el análisis completo
    const analysisRes = await fetch(
      `${OLLAMA_BASE_URL}/api/generate`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          model: 'llama3.2:3b',
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

    if (!analysisRes.ok) {
      const errorText = await analysisRes.text();
      console.error("Error from Ollama API (analysis):", errorText);
      return NextResponse.json(
        { error: 'Ollama request failed for analysis', details: errorText },
        { status: analysisRes.status }
      );
    }

    const analysisData = await analysisRes.json();
    const aiResponse = analysisData.response;

    // Llamada a la API de Ollama para el resumen con sugerencias
    const summaryRes = await fetch(
      `${OLLAMA_BASE_URL}/api/generate`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          model: 'llama3.2:3b',
          prompt: summaryPrompt,
          stream: false,
          options: {
            temperature: temperature + 0.1, // Ligeramente más creativo para sugerencias
            top_p,
            num_predict: 1024 // Menos tokens para el resumen
          }
        }),
      }
    );

    let summaryResponse = '';
    if (summaryRes.ok) {
      const summaryData = await summaryRes.json();
      summaryResponse = summaryData.response;
    } else {
      console.error("Error from Ollama API (summary):", await summaryRes.text());
      // Continuamos aunque falle el resumen
    }

    // Procesamos la respuesta para extraer las diferentes partes según el formato
    const processedResponse = processResponse(aiResponse);
    
    // Generamos una versión "mejorada" del documento
    const improvedDocument = generateImprovedDocument(pdfContent, processedResponse, summaryResponse);

    // Retornamos tanto la respuesta formateada como el documento mejorado
    return NextResponse.json({
      formattedResponse: processedResponse.fullResponse,
      improvedDocument: improvedDocument,
      summary: summaryResponse
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
  // Extraemos los componentes según el formato estructurado del análisis
  const titleMatch = response.match(/# Análisis del (.*?)(?=\n|$)/);
  const introMatch = response.match(/## Introducción\s*([\s\S]*?)(?=## Detalles|$)/);
  const detailsMatch = response.match(/## Detalles\s*([\s\S]*?)(?=## Conclusión|$)/);
  const conclusionMatch = response.match(/## Conclusión\s*([\s\S]*?)(?=$)/);

  const title = titleMatch ? `Análisis del ${titleMatch[1].trim()}` : 'Análisis de Documento';
  const introduction = introMatch ? introMatch[1].trim() : '';
  const details = detailsMatch ? detailsMatch[1].trim() : '';
  const conclusion = conclusionMatch ? conclusionMatch[1].trim() : '';

  console.log("Procesa la respuesta:", { title, intro: introduction.substring(0, 50), details: details.substring(0, 50) });

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
function generateImprovedDocument(
  originalContent: string, 
  analysis: {
    title: string;
    introduction: string;
    details: string;
    conclusion: string;
    fullResponse: string;
  },
  summaryResponse: string
) {
  // En una implementación real, se podrían aplicar modificaciones específicas 
  // basadas en el análisis. Por ahora, añadimos comentarios con las sugerencias.
  
  const lines = originalContent.split('\n');
  let improvedDocument = '';
  let currentSection = '';

  // Extraer sugerencias del resumen
  const suggestionMatch = summaryResponse.match(/## SUGERENCIAS DE MEJORA([\s\S]*?)(?=## PUNTOS CRÍTICOS|$)/);
  const suggestions = suggestionMatch ? suggestionMatch[1].trim() : '';
  
  const criticalPointsMatch = summaryResponse.match(/## PUNTOS CRÍTICOS([\s\S]*?)(?=$)/);
  const criticalPoints = criticalPointsMatch ? criticalPointsMatch[1].trim() : '';

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
      // Usamos las sugerencias específicas si están disponibles
      if (suggestions) {
        improvedDocument += `${suggestions}\n`;
      } else {
        improvedDocument += `${analysis.introduction}\n`;
      }
      improvedDocument += '*/\n\n';
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
  
  // Usamos los puntos críticos específicos si están disponibles
  if (criticalPoints) {
    improvedDocument += `PUNTOS CRÍTICOS QUE REQUIEREN ATENCIÓN INMEDIATA:\n${criticalPoints}\n\n`;
  }
  
  improvedDocument += `${analysis.conclusion}\n*/\n`;

  return improvedDocument;
}

export function GET() {
  return NextResponse.json({ message: 'Use POST to analyze a PDF' });
}
