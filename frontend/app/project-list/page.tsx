import ProjectList from "./project-list";
import { RoleProtectedPage } from "@/components/role-protected-page/role-protected-page";

export default function ProjectPage() {
  return (
    <RoleProtectedPage allowedRoles={["admin", "tutor"]}>
      <ProjectList />
    </RoleProtectedPage>
  );
}