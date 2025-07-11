import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { EstadoApiAdapter } from "@/lib/externalApi/estados";

export async function GET(_request: Request, { params }: { params: { id: number } }) {
  const token = (await cookies()).get("access_token")?.value;

  if (!token)
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  const { id } = params;

  const adapter = new EstadoApiAdapter(token);
  const estado = await adapter.obterEstadoPorId(id);
  return NextResponse.json(estado);
}
