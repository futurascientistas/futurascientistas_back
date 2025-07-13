import { useState, useEffect } from "react";
import { Project } from "@/types/project";

export function useEditProject(id: string) {
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [success, setSuccess] = useState<string | null>(null);

  // Fetch inicial do projeto

  const carregarProjeto = async (id: string) => {
    if (!id) {
      setProject(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`/api/projetos/${id}/`);
      if (!res.ok) throw new Error("Projeto não encontrado");
      const data: Project = await res.json();
      setProject(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    carregarProjeto(id)
  }, [id]);

  // Atualizar projeto
  async function atualizarProjeto(updated: Project) {
    setIsSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch(`/api/projetos/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updated),
      });

      const payload = await res.json();
      if (!res.ok) throw new Error(payload.error || "Erro ao atualizar");

      setProject(payload as Project);
      setSuccess("Projeto atualizado com sucesso!");
      return payload as Project;

    } catch (err: any) {
      setError(err.message);
      throw err;

    } finally {
      setIsSaving(false);
    }
  }

  return { project, isLoading, error, isSaving, success, atualizarProjeto };
}
