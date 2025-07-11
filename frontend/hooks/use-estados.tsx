"use client"

import { useState, useEffect } from "react"
import type { Estado } from "../types/estado"

export function useEstados() {
  const [estados, setEstados] = useState<Estado[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const carregarEstados = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/estados');
      if (!res.ok) throw new Error('Erro ao buscar estados');
      const data = await res.json();
      setEstados(data);

    } catch (err: any) {
      setError(err.message || 'Erro desconhecido');
    } finally {
      setIsLoading(false);
    }
    
  }

  const filtrarEstadosPorRegiao = (regiaoId: number) => {
    return estados.filter(estado => estado.regiao?.id === regiaoId); 
  }

  useEffect(() => {
    carregarEstados()
  }, [])

  return {
    estados,
    isLoading,
    error,
    recarregarEstados: carregarEstados,
    filtrarEstadosPorRegiao
  }
}
