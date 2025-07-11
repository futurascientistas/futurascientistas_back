import { RoleProtectedPage } from "@/components/role-protected-page/role-protected-page";
import { UserProfileForm } from "@/components/user-profile/user-profile-form";

export default function UserProfilePage() {
  return (
    <RoleProtectedPage allowedRoles={["estudante", "admin", "tutor"]}>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-800">Minha Conta</h1>
        <p className="text-gray-600">
          Gerencie suas informações pessoais e preferências de conta
        </p>

        <UserProfileForm />
      </div>
    </RoleProtectedPage>
  );
}
