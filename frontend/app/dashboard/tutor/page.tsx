"use client";

import { useEffect, useState } from "react";
import { RoleProtectedPage } from "@/components/role-protected-page/role-protected-page";

export default function DashboardTutorPage() {
  const [userName, setUserName] = useState("ANA PAULA");

  useEffect(() => {
    const storedUserName = localStorage.getItem("userName");
    if (storedUserName) {
      setUserName(storedUserName);
    }
  }, []);

  return (
    <RoleProtectedPage allowedRoles={["tutor"]}>
      <div className="space-y-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h1 className="text-xl font-semibold text-blue-800 mb-2">
            Bem-vinda ao Futuras Cientistas
          </h1>
          <p className="text-blue-600 text-sm">
            Navegue no menu ao lado para ter acesso às funcionalidades.
          </p>
        </div>
      </div>
    </RoleProtectedPage>
  );
}
