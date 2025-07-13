// app/api/projetos/todos/route.ts
export const dynamic = "force-dynamic";

import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { ProjectApiAdapter } from "@/lib/externalApi/projects";

export async function GET() {
  const token = (await cookies()).get('access_token')?.value;

  if (!token)
    return NextResponse.json({ error: 'Não autenticado' }, { status: 401 });

  const adapter = new ProjectApiAdapter(token);
  const projetos = await adapter.listarProjetos();

  return NextResponse.json(projetos);
}