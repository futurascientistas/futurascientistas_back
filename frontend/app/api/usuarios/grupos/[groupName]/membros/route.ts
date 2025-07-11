import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { GroupApiAdapter } from "@/lib/externalApi/groups";

export async function GET(_request: Request, { params }: { params: { groupName: string } }) {
  console.log('Rota de membros de tutor chamada', params.groupName);

    const token = (await cookies()).get("access_token")?.value;

  if (!token)
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  const { groupName } = params;

  console.log('Grupo: ', groupName)

  const adapter = new GroupApiAdapter(token);
  const membros = await adapter.listarMembrosPorGrupo(groupName);
  return NextResponse.json(membros);
}
