"use client"

import { useState, useEffect, useCallback } from "react"
import type { Project } from "@/types/project"
import type { FiltrosProjects } from "@/types/project"

export function useProjects() {
  const [projetos, setProjetos] = useState<Project[]>([])
  const [projetosFiltrados, setProjetosFiltrados] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [filtros, setFiltros] = useState<FiltrosProjects>({})

  const criarProjeto = async (projeto: Project) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null)

    try {
      const res = await fetch('/api/projetos/criar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(projeto),
      });

      if (!res.ok) {
        const errorData = await res.json();
        setError(errorData.error || 'Erro ao criar projeto');
        throw new Error(errorData.error || 'Erro ao criar projeto');
      }

      const novoProjeto = await res.json();
      setProjetos((prev) => [...prev, novoProjeto]);
      setProjetosFiltrados((prev) => [...prev, novoProjeto]);
      var message = `Projeto ${projeto.nome} criado com sucesso.`;
      setSuccess(message)

      console.log("Hook message: ", success)
    } catch (err: any) {
      setError(err.message || "Erro inesperado ao criar projeto");
      console.error("Erro no hook useProjects:", err);
    } finally {
      setIsLoading(false);
    }
  };


  const carregarProjetos = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/projetos/todos');
      if (!res.ok) throw new Error('Erro ao buscar projetos');
      const data = await res.json();
      setProjetos(data);
      setProjetosFiltrados(data);

    } catch (err: any) {
      setError(err.message || 'Erro desconhecido');
    } finally {
      setIsLoading(false);
    }
  }

  const aplicarFiltros = useCallback(async (filtrosAtivos: FiltrosProjects) => {
    setIsLoading(true)
    setFiltros(filtrosAtivos)
    setError(null)

    try {
      const query = new URLSearchParams();

      if (filtrosAtivos.titulo) query.append("nome", filtrosAtivos.titulo);
      if (filtrosAtivos.tutorId) query.append("tutora", filtrosAtivos.tutorId);
      if (filtrosAtivos.regiao) query.append("regiao", filtrosAtivos.regiao);
      if (filtrosAtivos.estado) query.append("estado", filtrosAtivos.estado);
      if (filtrosAtivos.cidade) query.append("cidade", filtrosAtivos.cidade);
      if (filtrosAtivos.formato) query.append("formato", filtrosAtivos.formato.toLowerCase());
      if (filtrosAtivos.instituicao) query.append("instituicao", filtrosAtivos.instituicao);
      if (filtrosAtivos.dataInicio) query.append("data_inicio", filtrosAtivos.dataInicio);
      if (filtrosAtivos.dataFim) query.append("data_fim", filtrosAtivos.dataFim);

      const response = await fetch(`/api/projetos/filter?${query.toString()}`);
      const data = await response.json();

      if (!response.ok) throw new Error(data.error || 'Erro ao filtrar projetos');
      
      setProjetosFiltrados(data);
      setProjetos(data);
      setError(null);

    } catch (err: any) {
      setError("Erro inesperado ao filtrar projetos")
      console.error("Erro ao filtrar projetos:", err)
    } finally {
      setIsLoading(false)
    }
  }, []);

  const limparFiltros = () => {
    setFiltros({})
    carregarProjetos()
  }

  useEffect(() => {
    carregarProjetos()
  }, [])

  return {
    projetos: projetosFiltrados,
    isLoading,
    error,
    success,
    filtros,
    criarProjeto,
    recarregarProjetos: carregarProjetos,
    aplicarFiltros,
    limparFiltros,
    totalProjetos: projetos.length,
    projetosFiltrados: projetosFiltrados.length,
  }
}
