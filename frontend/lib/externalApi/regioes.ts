import axiosInstance from "@/lib/axios";
import { Regiao } from "@/types/regiao";
import API_ENDPOINTS from "./endpoints";

export class RegiaoApiAdapter {
  constructor(private token: string) {}

  async listarRegioes(): Promise<Regiao[]> {
    const response = await axiosInstance.get(API_ENDPOINTS.REGIOES, {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    return response.data.map(mapRegiao);
  }

  async obterRegiaoPorId(id: number): Promise<Regiao> {
    // console.log("URL da requisição:", API_ENDPOINTS.regiaoPorID(id));
    const response = await axiosInstance.get(API_ENDPOINTS.regiaoPorID(id), {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    return mapRegiao(response.data);
  }
}

export function mapRegiao(data: any): Regiao {
  return {
    id: data.id,
    nome: data.nome,
    abreviacao: data.abreviacao,
    descricao: data.descricao,
  };
}
