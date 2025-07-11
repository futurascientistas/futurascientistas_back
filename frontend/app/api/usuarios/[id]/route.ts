import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { UserApiAdapter } from "@/lib/externalApi/users";

export async function GET(_request: Request, { params }: { params: { id: string } }) {
  const token = (await cookies()).get("access_token")?.value;

  if (!token)
    return NextResponse.json({ error: "Não autenticado" }, { status: 401 });
  const { id } = params;

  const adapter = new UserApiAdapter(token);
  const user = await adapter.obterUserPorId(id);
  return NextResponse.json(user);
}
