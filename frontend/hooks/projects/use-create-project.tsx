"use client"

import { useState, useEffect } from "react"
import type { Project } from "@/types/project"

export function useCreateProject() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const criarProjeto = async (projeto: Project) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null)

    console.log("Project hook", projeto)

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

  return {
    isLoading,
    error,
    success,
    criarProjeto,
  }
}
