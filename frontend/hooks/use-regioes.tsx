"use client"

import { useState, useEffect } from "react"
import type { Regiao } from "../types/regiao"

export function useRegioes() {
  const [regioes, setRegioes] = useState<Regiao[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const carregarRegioes = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/regioes');
      if (!res.ok) throw new Error('Erro ao buscar regioes');
      const data = await res.json();
      setRegioes(data);

    } catch (err: any) {
      setError(err.message || 'Erro desconhecido');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    carregarRegioes()
  }, [])

  return {
    regioes,
    isLoading,
    error,
    recarregarRegioes: carregarRegioes,
  }
}
