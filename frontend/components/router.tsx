"use client";
import { useAuth } from "@/hooks/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

const Router = () => {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user == null) {
      router.push("/login"); // Usuário não existe
    } else if (user && user.password_needs_reset == true) {
      router.push("/redefinir-senha"); // Usuário precisa resetar a senha
    } else {
      // Redirect based on role
      switch (user.role) {
        case "estudante":
        case "professora":
          router.push("/dashboard/estudante");
          break;
        case "avaliadora":
          router.push("/dashboard/tutor");
          break;
        case "admin":
          console.log("Redirecionando para admin");
          router.push("/dashboard/admin");
          break;
      }
    }
  }, [user, router]);

  return null; // Não renderiza nada, apenas redireciona
};

export default Router;
