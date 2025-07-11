import ProtectedPage from "@/components/protected-page";
import PasswordResetForm from "../../password-reset-form";

export default function PasswordResetPage() {
  return (
    <ProtectedPage>
      <PasswordResetForm />
    </ProtectedPage>
  );
}
