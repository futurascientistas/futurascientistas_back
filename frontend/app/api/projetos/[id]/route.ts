// app/api/projetos/[id]/route.ts

import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { ProjectApiAdapter } from '@/lib/externalApi/projects'
import type { NextRequest } from 'next/server'

export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest, context: { params: { id: string } }) {
    const { id } = context.params;
  const token = (await cookies()).get('access_token')?.value
  if (!token) {
    return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
  }

  try {
    const adapter = new ProjectApiAdapter(token)
    const projeto = await adapter.getProjetoPorId(id)
    return NextResponse.json(projeto)
  } catch (err: any) {
    console.error('Erro ao buscar projeto:', err)
    return NextResponse.json({ error: err.message || 'Erro interno' }, { status: 500 })
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const token = (await cookies()).get('access_token')?.value
  if (!token) {
    return NextResponse.json({ error: 'Não autenticado' }, { status: 401 })
  }

  let body: any
  try {
    body = await request.json()
  } catch {
    return NextResponse.json({ error: 'Corpo inválido' }, { status: 400 })
  }

  try {
    const adapter = new ProjectApiAdapter(token)
    const updated = await adapter.atualizarProjeto(params.id, body)
    return NextResponse.json(updated)
  } catch (err: any) {
    console.error('Erro ao atualizar projeto:', err)
    const status = err.response?.status || 500
    const message = err.response?.data?.error || err.message || 'Erro interno'
    return NextResponse.json({ error: message }, { status })
  }
}
