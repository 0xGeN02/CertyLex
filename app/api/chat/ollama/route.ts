import { NextResponse } from 'next/server';

const OLLAMA_BASE_URL = process.env.OLLAMA_HOST || 'http://localhost:11434';

export async function POST(request: Request) {
  try {
    const { model, messages } = await request.json();
    const prompt = messages.map((m: any) => m.content).join('\n');

    const res = await fetch(
      `${OLLAMA_BASE_URL}/api/generate`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model, prompt, stream: true }),
      }
    );

    if (!res.ok) {
      return NextResponse.json(
        { error: 'Ollama chat request failed' },
        { status: res.status }
      );
    }

    // Acumula las respuestas aquí
    const response: string[] = [];

    if (!res.body) {
      return NextResponse.json(
        { error: 'ReadableStream not yet supported in this environment' },
        { status: 500 }
      );
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      for (const line of chunk.split('\n').filter(Boolean)) {
        try {
          const json = JSON.parse(line);
          if (json.response !== undefined) {
            response.push(json.response);
            console.log('Palabra:', json.response);
          }
        } catch (err) {
          console.error('JSON parse error:', err);
        }
      }
    }

    // Envía el array completo al frontend
    return NextResponse.json({ response });

  } catch (e) {
    console.error('Chat error:', e);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export function GET() {
  return NextResponse.json({ message: 'Use POST to chat' });
}