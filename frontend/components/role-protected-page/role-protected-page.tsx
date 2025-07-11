"use client";
import { useAuth } from "@/hooks/auth-context";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Header from "@/components/header/header";
import SidebarItems from "@/components/dashboard/sidebar/sidebar-items";
import styles from "./roleprotectedpage.module.css";

type RoleProtectedProps = {
  allowedRoles: string[]; // Ex: ['admin']
  children: React.ReactNode;
  redirectTo?: string; // Para onde redirecionar quem não tem acesso
};

export function RoleProtectedPage({
  allowedRoles,
  children,
  redirectTo = "/login",
}: RoleProtectedProps) {
  const { user, loading } = useAuth();
  const router = useRouter();

  const [activeMenuItem, setActiveMenuItem] = useState("cadastro");

  const handleMenuItemClick = (item: string) => {
    setActiveMenuItem(item);
  };

  const renderSidebar = () => {
    return (
      <SidebarItems
        activeItem={activeMenuItem}
        onItemClick={handleMenuItemClick}
      />
    );
  };

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.replace("/login");
      } else if (!allowedRoles.includes(user.role)) {
        router.replace(redirectTo);
      }
    }
  }, [user, loading, allowedRoles, redirectTo, router]);

  if (loading || !user || !allowedRoles.includes(user.role))
    return <div>Carregando...</div>;

  return (
    <>
      <Header />
      {renderSidebar()}

      <div className={styles.container}>
        <div className={styles.contentWrapper}>
          {children}
        </div>
      </div>
      
    </>
  );
}
