import { NextResponse } from 'next/server';

export async function GET() {
  const data = { message: 'Hello from Next.js API!' };
  return NextResponse.json(data);
}