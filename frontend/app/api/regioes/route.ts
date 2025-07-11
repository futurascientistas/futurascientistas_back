export const dynamic = "force-dynamic";

import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { RegiaoApiAdapter } from "@/lib/externalApi/regioes";

export async function GET() {
  const token = (await cookies()).get('access_token')?.value;

  if (!token)
    return NextResponse.json({ error: 'Não autenticado' }, { status: 401 });

  const adapter = new RegiaoApiAdapter(token);
  const regioes = await adapter.listarRegioes();
  return NextResponse.json(regioes);
}