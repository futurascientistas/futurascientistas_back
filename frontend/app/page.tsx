"use client"

import { redirect } from "next/navigation"
import { useAuth } from "@/hooks/auth-context"

export default function Home() {
  const { logout } = useAuth()
  logout() // Logout do usuário

  redirect("/lading-page")
}
