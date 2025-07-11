import axios from 'axios';
import type { UserApiResponse } from "../types/project"

const API_URL = 'http://localhost:8000/auth/usuario/';

export class UserService {
  static async listarTutores(): Promise<UserApiResponse> {
    try {
      // Simulação de dados para o preview funcionar
      const tutoresMock = [
        { id: "1", nome: "Dra. Maria Silva", email: "maria.silva@universidade.edu.br", perfil: "Professor" },
        { id: "2", nome: "Prof. João Santos", email: "joao.santos@instituto.org.br", perfil: "Professor" },
        { id: "3", nome: "Dra. Ana Costa", email: "ana.costa@pesquisa.gov.br", perfil: "Professor" },
        { id: "4", nome: "Prof. Carlos Lima", email: "carlos.lima@universidade.edu.br", perfil: "Professor" },
        { id: "5", nome: "Dra. Fernanda Oliveira", email: "fernanda.oliveira@instituto.org.br", perfil: "Professor" },
        { id: "6", nome: "Prof. Ricardo Pereira", email: "ricardo.pereira@pesquisa.gov.br", perfil: "Professor" },
        {
          id: "7",
          nome: "Dra. Juliana Rodrigues",
          email: "juliana.rodrigues@universidade.edu.br",
          perfil: "Professor",
        },
        { id: "8", nome: "Prof. Eduardo Martins", email: "eduardo.martins@instituto.org.br", perfil: "Professor" },
      ]

      // Simular delay da API
      await new Promise((resolve) => setTimeout(resolve, 300))

      return {
        success: true,
        message: "Tutores carregados com sucesso",
        data: tutoresMock,
      }
    } catch (error) {
      console.error("Erro ao carregar tutores:", error)
      return {
        success: false,
        message: "Erro de conexão com o servidor",
        error: error instanceof Error ? error.message : "Erro desconhecido",
      }
    }
  }

  static async buscarTutores(termo: string): Promise<UserApiResponse> {
    try {
      const response = await this.listarTutores()

      if (response.success && response.data) {
        const tutoresFiltrados = response.data.filter(
          (tutor) =>
            tutor.nome.toLowerCase().includes(termo.toLowerCase()) ||
            tutor.email.toLowerCase().includes(termo.toLowerCase()),
        )

        return {
          success: true,
          message: "Busca realizada com sucesso",
          data: tutoresFiltrados,
        }
      }

      return response
    } catch (error) {
      console.error("Erro ao buscar tutores:", error)
      return {
        success: false,
        message: "Erro na busca de tutores",
        error: error instanceof Error ? error.message : "Erro desconhecido",
      }
    }
  }
}

export async function getUserData(userId: string): Promise<{ success: boolean; data?: any; message?: string }> {
  try {
    const response = await axios.get(`${API_URL}${userId}/`);
    return { success: true, data: response.data };
  } catch (error: any) {
    return {
      success: false,
      message:
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.response?.data?.mensagem ||
        error.message ||
        'Erro desconhecido',
    };
  }
}

export async function updateUserData(userId: string, userData: any): Promise<{ success: boolean; message?: string }> {
  try {
    const response = await axios.put(`${API_URL}editar/${userId}/`, userData);
    return { success: true, message: response.data.message };
  } catch (error: any) {
    return {
      success: false,
      message:
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.response?.data?.mensagem ||
        error.message ||
        'Erro desconhecido',
    };
  }
}