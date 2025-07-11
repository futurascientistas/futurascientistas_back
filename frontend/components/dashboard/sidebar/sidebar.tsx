"use client";

import { useAuth } from "@/hooks/auth-context";
import { useState } from "react"
import SidebarItems from "./sidebar-items";

export default function Sidebar() {
  const { user } = useAuth();
  const [activeMenuItem, setActiveMenuItem] = useState("cadastro")

  if (!user) return null;

  const handleMenuItemClick = (item: string) => {
    setActiveMenuItem(item)
  }

  return <SidebarItems activeItem={activeMenuItem} onItemClick={handleMenuItemClick} />
}