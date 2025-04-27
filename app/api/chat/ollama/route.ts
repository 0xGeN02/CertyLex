import { NextResponse } from 'next/server';

const OLLAMA_BASE_URL = process.env.OLLAMA_HOST || 'http://localhost:11434';

export async function POST(request: Request) {
  try {
    const { model, messages } = await request.json();
    // Build prompt from incoming messages
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

    // Transform NDJSON → SSE (`data: …\n\n`)
    const sseStream = new ReadableStream({
      async start(controller) {
        if (!res.body) {
          controller.error(new Error('ReadableStream not yet supported in this environment'));
          return;
        }
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        const encoder = new TextEncoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          for (const line of chunk.split('\n').filter(Boolean)) {
            controller.enqueue(encoder.encode(`data: ${line}\n\n`));
            console.log('Chunk:', line);
          }
        }
        controller.close();
      },
    });

    console.log('Model response:', sseStream); // Chunk: {"model":"llama3.2:3b","created_at":"2025-04-27T22:26:30.080840908Z","response":"Hola","done":false}
    return new NextResponse(sseStream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
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