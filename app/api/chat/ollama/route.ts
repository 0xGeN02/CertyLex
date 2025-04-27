import { NextResponse } from 'next/server';

const OLLAMA_BASE_URL = process.env.OLLAMA_HOST || 'http://localhost:11434';

export async function POST(request: Request) {
  try {
    const { model, messages } = await request.json();
    // Envía la conversación al endpoint de Ollama con streaming
    const res = await fetch(
      `${OLLAMA_BASE_URL}/api/chat/${encodeURIComponent(model)}?stream=true`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages })
      }
    );

    if (!res.ok) {
      return NextResponse.json(
        { error: 'Ollama chat request failed' },
        { status: res.status }
      );
    }

    // Reenvía el body como text/event-stream
    return new NextResponse(res.body, {
      headers: { 'Content-Type': 'text/event-stream' }
    });
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