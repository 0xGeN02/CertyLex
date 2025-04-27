import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";  // usa Node.js runtime para fetch
export const revalidate = 0;      // sin cache

const HOST = process.env.OLLAMA_HOST ?? "http://localhost:11434";
if (!HOST) {
    throw new Error("OLLAMA_HOST no está definido");
}

/**
 * GET /api/chat/ollama
 * → Lista modelos locales vía GET /api/tags de Ollama
 */
export async function GET() {
  const res = await fetch(`${HOST}/api/tags`);
  if (!res.ok) {
    return NextResponse.json(
      { error: "Error al obtener modelos de Ollama" },
      { status: res.status }
    );
  }
  const models = await res.json();  // array de objetos { name, size, … }
  return NextResponse.json({ models });
}

/**
 * POST /api/chat/ollama
 * → Proxea chat al modelo seleccionado
 * Body esperado: { model: string, messages: { role: string, content: string }[] }
 */
export async function POST(request: NextRequest) {
  const { model, messages } = await request.json();

  const ollamaRes = await fetch(
    `${HOST}/api/chat`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model,
        messages,
        stream: true  // habilita streaming :contentReference[oaicite:3]{index=3}
      }),
    }
  );

  if (!ollamaRes.ok) {
    const error = await ollamaRes.text();
    return new Response(error, { status: ollamaRes.status });
  }

  // Forward streaming response al cliente (text/event-stream)
  return new Response(ollamaRes.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
    },
  });
}
