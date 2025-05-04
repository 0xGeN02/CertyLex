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
        body: JSON.stringify({ model, prompt, stream: false }), // Changed stream to false
      }
    );

    if (!res.ok) {
      const errorText = await res.text();
      console.error("Error from Ollama API:", errorText);
      return NextResponse.json(
        { error: 'Ollama chat request failed', details: errorText },
        { status: res.status }
      );
    }

    const data = await res.json(); // Parse the response as JSON

    // Return the response directly to the frontend
    return NextResponse.json({ response: data.response });

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