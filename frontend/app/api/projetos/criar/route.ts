import { ProjectApiAdapter } from "@/lib/externalApi/projects";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";


export async function POST(request: Request) {
  const token = (await cookies()).get('access_token')?.value;

  if (!token) {
    return NextResponse.json({ error: 'Não autenticado' }, { status: 401 });
  }

  let projeto;
  try {
    projeto = await request.json();
  } catch {
    return NextResponse.json({ error: 'Dados inválidos no corpo da requisição' }, { status: 400 });
  }

  try {
    const adapter = new ProjectApiAdapter(token);
    const novoProjeto = await adapter.criarProjeto(projeto);
    return NextResponse.json(novoProjeto);
  } catch (error: any) {
    console.error("Erro ao criar projeto:", error);
    return NextResponse.json({ error: error.message || 'Erro ao criar projeto' }, { status: 500 });
  }
}
