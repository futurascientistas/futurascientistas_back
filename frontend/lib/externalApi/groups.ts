import axiosInstance from "@/lib/axios";
import { User, UserProfile } from "@/types/user";
import API_ENDPOINTS from "./endpoints";
import { group } from "console";

export class GroupApiAdapter {
  constructor(private token: string) {}

  async listarMembrosPorGrupo(groupName: string): Promise<User[]> {
    console.log("Adptar group name", groupName)
    
    const response = await axiosInstance.get(API_ENDPOINTS.membrosPorGrupo(groupName), {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    if (!response.data) {
      throw new Error("Nenhum membro encontrado para o grupo informado.");
    }

    return response.data.map((user: any, groupName) => this.mapUser(user, groupName));
  }

  private mapUser(data: any, profile: UserProfile): User {
    return {
        id: data.id,
        name: data.name,
        email: data.email,
        cpf: data.cpf,
        profile: profile,
        perfil: ""
    };
  }
}
