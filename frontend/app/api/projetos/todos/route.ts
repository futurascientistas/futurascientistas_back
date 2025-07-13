// app/api/projetos/todos/route.ts

export const dynamic = "force-dynamic";

import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { ProjectApiAdapter } from "@/lib/externalApi/projects";
import { EstadoApiAdapter } from "@/lib/externalApi/estados";
import { RegiaoApiAdapter } from "@/lib/externalApi/regioes";
import { UserApiAdapter } from "@/lib/externalApi/users";

export async function GET() {
  const token = (await cookies()).get('access_token')?.value;

  if (!token)
    return NextResponse.json({ error: 'Não autenticado' }, { status: 401 });

  const adapter = new ProjectApiAdapter(token);
  const projetos = await adapter.listarProjetos();

  // const estadoAdapter = new EstadoApiAdapter(token);
  // const regiaoAdapter = new RegiaoApiAdapter(token);
  // const userAdapter = new UserApiAdapter(token);
  // const projetosComEstado = await Promise.all(
  //   projetos.map(async (projeto) => {
  //     const regiao = projeto.regiaoID
  //       ? await regiaoAdapter.obterRegiaoPorId(projeto.regiaoID)
  //       : undefined;

  //     const estado = projeto.estadoID
  //       ? await estadoAdapter.obterEstadoPorId(projeto.estadoID)
  //       : undefined;

  //     const cidade = projeto.cidadeID
  //       ? await estadoAdapter.obterCidadePorId(projeto.cidadeID)
  //       : undefined;

  //     const tutor = projeto.tutorID
  //     ? await userAdapter.obterUserPorId(projeto.tutorID)
  //     : undefined;

  //     return {
  //       ...projeto,
  //       regiao,
  //       estado,
  //       cidade,
  //       tutor
  //     };
  //   })
  // );

  return NextResponse.json(projetos);
}