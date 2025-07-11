export const dynamic = "force-dynamic";

import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { EstadoApiAdapter } from "@/lib/externalApi/estados";

export async function GET() {
  const token = (await cookies()).get('access_token')?.value;

  if (!token)
    return NextResponse.json({ error: 'Não autenticado' }, { status: 401 });

  const adapter = new EstadoApiAdapter(token);
  const estados = await adapter.listarEstados();
  return NextResponse.json(estados);
}