// app/api/projetos/filter/route.ts
export const dynamic = "force-dynamic";

import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { ProjectApiAdapter } from "@/lib/externalApi/projects";

export async function GET(request: NextRequest) {
  const token = (await cookies()).get('access_token')?.value;

  if(!token)
    return NextResponse.json({ error: 'Não autenticado' }, { status: 401 });

  try {
    const queryParams = request.nextUrl.searchParams;
    const adapter = new ProjectApiAdapter(token);
    const projetosFiltrados = await adapter.filtrarProjetos(queryParams);
    return NextResponse.json(projetosFiltrados);

  } catch(error) {
    return NextResponse.json(
      { error: error.message || "Erro ao buscar projetos" },
      { status: 500 }
    );
  }
}

// http://127.0.0.1:8000/projetos/todos/?regioes_aceitas=Sul,Norte