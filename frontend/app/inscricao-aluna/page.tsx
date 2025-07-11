import InscricaoPage from "./inscricao-aluna-form";
import { RoleProtectedPage } from "@/components/role-protected-page/role-protected-page";

export default function ProjectPage() {
  return (
    <RoleProtectedPage allowedRoles={["admin", "tutor", "estudante"]}>
      <InscricaoPage />
    </RoleProtectedPage>
  );
}
