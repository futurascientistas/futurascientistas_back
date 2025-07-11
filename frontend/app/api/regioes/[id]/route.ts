import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { RegiaoApiAdapter } from "@/lib/externalApi/regioes";

export async function GET(_request: Request, { params }: { params: { id: number } }) {
  const token = (await cookies()).get("access_token")?.value;

  if (!token)
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  const { id } = params;

  const adapter = new RegiaoApiAdapter(token);
  const regiao = await adapter.obterRegiaoPorId(id);
  return NextResponse.json(regiao);
}
