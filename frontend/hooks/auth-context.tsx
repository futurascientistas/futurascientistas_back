"use client";
import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import axios from "axios";

type UserType = {
  id: number;
  nome: string;
  email: string;
  cpf: string;
  password_needs_reset: boolean;
  groups: string[];
  role: string; // Ex: 'estudante', 'professora', 'avaliadora', 'admin' (based on user group)
};

type AuthContextType = {
  user: UserType | null;
  loading: boolean;
  refreshUser: () => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const API_URL = "http://localhost:8000/usuarios/auth/";

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserType | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}profile/`, {
        withCredentials: true,
      });

      // Define role based on the first group
      const responseUser = res.data;
      responseUser.role = responseUser.groups?.[0] || null;

      setUser(responseUser);
    } catch {
      setUser(null);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchUser();
  }, []);

  // Use para forçar revalidação do usuário (ex: após login/logout)
  const refreshUser = () => fetchUser();

  const logout = async () => {
    await axios.post(`${API_URL}logout/`, {}, { withCredentials: true });
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, refreshUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth precisa ser usado dentro do AuthProvider!");
  return context;
}
