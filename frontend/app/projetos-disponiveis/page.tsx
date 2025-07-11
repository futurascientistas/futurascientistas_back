import { ProjetosDisponiveis } from "./projetos-disponiveis";
import { RoleProtectedPage } from "@/components/role-protected-page/role-protected-page";

export default function ProjectPage() {
  return (
    <RoleProtectedPage allowedRoles={["estudante"]}>
      <ProjetosDisponiveis />
    </RoleProtectedPage>
  );
}