import axiosInstance from "@/lib/axios";
import { User } from "@/types/user";
import API_ENDPOINTS from "./endpoints";

export class UserApiAdapter {
  constructor(private token: string) {}

  async obterUserPorId(id: string): Promise<User> {
    const response = await axiosInstance.get(API_ENDPOINTS.userPorID(id), {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    return {
        id: response.data.id,
        name: response.data.nome
    };
  }
}
