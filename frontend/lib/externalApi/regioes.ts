import axiosInstance from "@/lib/axios";
import { Regiao } from "@/types/regiao";
import API_ENDPOINTS from "./endpoints";

export class RegiaoApiAdapter {
  constructor(private token: string) {}

  async listarRegioes(): Promise<Regiao[]> {
    const response = await axiosInstance.get(API_ENDPOINTS.REGIOES, {
      headers: {
        Authorization: `Bearer ${this.token}`,
      }
    });

    return response.data.map(mapRegiao);
  }

  async obterRegiaoPorId(id: number): Promise<Regiao> {
    if(!id)
      return null
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.regiaoPorID(id), {
        headers: {
          Authorization: `Bearer ${this.token}`,
        },
      });

      var result = mapRegiao(response.data);
      return result;
    }catch(ex) {
      console.log("Exception:", ex);
    }
    
    return null;
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
