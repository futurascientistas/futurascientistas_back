import ProjectForm from "./project-form";
import { RoleProtectedPage } from "@/components/role-protected-page/role-protected-page";

export default function ProjectPage() {
  return (
    <RoleProtectedPage allowedRoles={["admin", "tutor"]}>
      <ProjectForm />
    </RoleProtectedPage>
  );
}
