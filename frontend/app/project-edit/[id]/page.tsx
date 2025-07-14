
import EditarProjeto from "./project-edit";
import { RoleProtectedPage } from "@/components/role-protected-page/role-protected-page";

interface PageProps {
  params: Promise<{ id: string }>
}

export default async function ProjectEditPage({ params }: PageProps) {
  const { id: id } = await params

  return (
    <RoleProtectedPage allowedRoles={["admin", "tutor"]}>
      <EditarProjeto projectId={id} />
    </RoleProtectedPage>
  );
}


