"use client"

import { useState, useEffect, use } from "react"
import { User } from "@/types/user"

export function useUsers(groupName: string = "") {
  const [users, setUsers] = useState<User[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadUsers = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/usuarios');
      if (!res.ok) throw new Error('Erro ao buscar usuários');
      const data = await res.json();
      setUsers(data);
    } catch (err: any) {
      setError(err.message || 'Erro desconhecido');
    } finally {
      setIsLoading(false);
    }
  }

  const loadUsersByGroup = async (groupName: string) => {
    setIsLoading(true) 
    setError(null)

    try {
      const res = await fetch(`/api/usuarios/grupos/${groupName}/membros`);
      if (!res.ok) throw new Error('Erro ao buscar usuários');
      const data = await res.json();
      setUsers(data);
    } catch (err: any) {
      setError(err.message || 'Erro desconhecido');
    } finally {
      setIsLoading(false);
    }
  }

  const searchUsers = (query: string) => {
    var filteredUsers = users.filter(user => user.name.toLowerCase().includes(query.toLowerCase()));
    return filteredUsers;
  }

  useEffect(() => {
    loadUsersByGroup(groupName)
  }, [groupName]);

  return {
    users,
    isLoading,
    error,
    recarregarUsers: loadUsers,
    loadUsersByGroup,
    searchUsers
  }
}
