import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { EstadoApiAdapter } from "@/lib/externalApi/estados";

export async function GET(_request: Request, { params }: { params: { uf: string } }) {
  const token = (await cookies()).get("access_token")?.value;

  if (!token)
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  const { uf } = params;

  const adapter = new EstadoApiAdapter(token);
  const cidades = await adapter.listarCidadesPorEstado(uf);
  return NextResponse.json(cidades);
}
