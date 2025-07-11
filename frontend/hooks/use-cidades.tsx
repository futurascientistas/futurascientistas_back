"use client";

import { useState, useEffect } from "react";
import type { Cidade } from "../types/cidade";

export function useCidades(uf: string) {
  const [cidades, setCidades] = useState<Cidade[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const carregarCidadesPorEstado = async (uf: string) => {
    if (!uf) {
      setCidades([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`/api/estados/${uf}/cidades`);
      if (!res.ok) throw new Error('Erro ao buscar cidades');
      const data = await res.json();
      setCidades(data);

    } catch (err: any) {
      setError(err.message || 'Erro desconhecido');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    carregarCidadesPorEstado(uf);
  }, [uf]);

  return {
    cidades,
    isLoading,
    error
  };
}
