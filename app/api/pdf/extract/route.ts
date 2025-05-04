import { NextRequest, NextResponse } from 'next/server';
import { join } from 'path';
import { writeFile } from 'fs/promises';
import { v4 as uuidv4 } from 'uuid';

export const config = {
  api: {
    bodyParser: false,
  },
};

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file || !file.name.endsWith('.pdf')) {
      return NextResponse.json({ error: 'Archivo inválido. Por favor, sube un PDF.' }, { status: 400 });
    }

    // Guardar el archivo en una ubicación temporal
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    
    // Genera un nombre único para el archivo temporal
    const tempFileName = `${uuidv4()}.pdf`;
    const tempFilePath = join('/tmp', tempFileName);
    
    // Escribir el archivo a disco
    await writeFile(tempFilePath, buffer);
    
    // Extrae el texto usando un servicio externo o una biblioteca
    // Por simplicidad, este ejemplo simula la extracción devolviendo un texto de ejemplo
    // En un entorno real, usarías algo como pdf.js, pdftotext, o un servicio de OCR
    
    // Simulación de extracción de texto
    const text = await simulatePdfTextExtraction(tempFilePath, file.name);
    
    return NextResponse.json({ text });
  } catch (error) {
    console.error('Error procesando el PDF:', error);
    return NextResponse.json({ error: 'Error al procesar el archivo' }, { status: 500 });
  }
}

// Función que simula la extracción de texto de un PDF
// En un entorno real, implementarías la extracción real con pdf.js o similar
async function simulatePdfTextExtraction(filePath: string, fileName: string) {
  // En una implementación real, aquí usarías una biblioteca como pdf.js
  // o una llamada a un servicio externo para extraer el texto
  
  // Por ahora, simplemente devuelve un texto de ejemplo basado en el nombre del archivo
  return `
CONTRATO DE PRESTACIÓN DE SERVICIOS PROFESIONALES

En Madrid, a 4 de Mayo de 2025

REUNIDOS

De una parte, DON JOSÉ GARCÍA LÓPEZ, mayor de edad, con domicilio en Calle Mayor 25, 28001 Madrid, y con DNI número 12345678A, actuando en su propio nombre y derecho (en adelante, el "CLIENTE").

Y de otra parte, DOÑA MARÍA RODRÍGUEZ SÁNCHEZ, mayor de edad, con domicilio profesional en Avenida de la Constitución 15, 28002 Madrid, y con DNI número 87654321B, actuando en su propio nombre y derecho (en adelante, el "PROFESIONAL").

Ambas partes (en adelante, conjuntamente, las "Partes"), reconociéndose mutuamente capacidad legal suficiente para contratar y obligarse en la representación que actúan y siendo responsables de la veracidad de sus manifestaciones,

EXPONEN

I. Que el CLIENTE está interesado en contratar los servicios profesionales del PROFESIONAL, consistentes en asesoramiento legal en materia contractual.

II. Que el PROFESIONAL tiene los conocimientos y la experiencia necesarios para prestar dichos servicios.

III. Que las Partes están interesadas en celebrar un contrato de prestación de servicios en virtud del cual el PROFESIONAL preste al CLIENTE los servicios que aquí se definen.

IV. Que las Partes han acordado otorgar el presente contrato de prestación de servicios profesionales (en adelante, el "Contrato"), con sujeción a las siguientes:

CLÁUSULAS

PRIMERA.- OBJETO
El objeto del presente Contrato es la prestación por parte del PROFESIONAL al CLIENTE de servicios de asesoramiento legal en materia contractual (en adelante, los "Servicios").

SEGUNDA.- DURACIÓN
El presente Contrato tendrá una duración de 12 meses, comenzando a surtir efectos en la fecha de su firma. 

TERCERA.- HONORARIOS
El CLIENTE abonará al PROFESIONAL, como contraprestación por los Servicios, la cantidad de CIEN EUROS (100 €) por hora de trabajo, con un mínimo de 10 horas mensuales.

CUARTA.- FORMA DE PAGO
El pago de los honorarios se realizará mediante transferencia bancaria a la cuenta que indique el PROFESIONAL, dentro de los primeros cinco días de cada mes.

QUINTA.- OBLIGACIONES DEL PROFESIONAL
El PROFESIONAL se compromete a:
- Prestar los Servicios con diligencia y profesionalidad.
- Mantener informado al CLIENTE del desarrollo de su actividad.
- Guardar secreto sobre toda la información que reciba del CLIENTE.

SEXTA.- OBLIGACIONES DEL CLIENTE
El CLIENTE se compromete a:
- Facilitar al PROFESIONAL toda la información necesaria para la correcta prestación de los Servicios.
- Abonar los honorarios acordados en el plazo establecido.

SEPTIMA.- RESOLUCIÓN DEL CONTRATO
Este contrato no podrá ser resuelto por ninguna de las partes.

OCTAVA.- LEY APLICABLE Y JURISDICCIÓN
El presente Contrato se regirá e interpretará de acuerdo con las leyes españolas.

Para la resolución de cualquier controversia que pudiera surgir en relación con la validez, interpretación, cumplimiento o resolución del presente Contrato, las Partes, con renuncia expresa a cualquier otro fuero que pudiera corresponderles, se someten al arbitraje.

Y en prueba de conformidad, las Partes firman el presente Contrato por duplicado y a un solo efecto, en el lugar y fecha indicados en el encabezamiento.

EL CLIENTE                                    EL PROFESIONAL
________________                       ________________
  `;
}

export function GET() {
  return NextResponse.json({ message: 'Usa POST para enviar un PDF' });
}
