"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ProjectService } from "@/services/projectService";
import EdicaoProjeto from "./project-edit";
import type { ProjectListItem, ProjectFormData } from "@/types/project";
import { RoleProtectedPage } from "@/components/role-protected-page/role-protected-page";

export default function ProjectEditPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = searchParams.get("id");

  const [projeto, setProjeto] = useState<ProjectListItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;

    ProjectService.getProjectById(id)
      .then((res) => setProjeto(res))
      .catch((err) => {
        console.error(err);
        router.push("/project-list");
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleSalvar = async (dados: ProjectFormData) => {
    try {
      if (!id) return;
      await ProjectService.updateProjeto(id, dados);
      router.push("/project-list");
    } catch (err) {
      console.error("Erro ao salvar projeto:", err);
      // exibir feedback para usuário se quiser
    }
  };

  if (loading) return <p>Carregando projeto...</p>;
  if (!projeto) return <p>Projeto não encontrado.</p>;

  return (
    <RoleProtectedPage allowedRoles={["admin", "tutor"]}>
      <EdicaoProjeto
        projeto={projeto}
        onVoltar={() => router.push("/project-list")}
        onSalvar={handleSalvar}
      />
    </RoleProtectedPage>
  );
}
