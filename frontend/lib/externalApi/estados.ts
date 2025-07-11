import axiosInstance from "@/lib/axios";
import { Estado } from "@/types/estado";
import { Regiao } from "@/types/regiao";
import { Cidade } from "@/types/cidade";
import { mapRegiao } from "./regioes";
import API_ENDPOINTS from "./endpoints";

export class EstadoApiAdapter {
  constructor(private token: string) {}

  async listarEstados(): Promise<Estado[]> {
    const response = await axiosInstance.get(API_ENDPOINTS.ESTADOS, {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    var result = response.data.map(this.mapEstado);

    return result;
  }

  async listarCidadesPorEstado(uf: string): Promise<Estado> {
    const response = await axiosInstance.get(API_ENDPOINTS.cidadesPorEstado(uf), {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    if (!response.data) {
      throw new Error("Nenhuma cidade encontrada para o estado informado.");
    }

    const cidades = response.data;
    return cidades.map((cidade: any) => this.mapCidade(cidade));
  }

  async obterEstadoPorId(id: number): Promise<Estado> {
    const response = await axiosInstance.get(API_ENDPOINTS.estadoPorID(id), {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    return this.mapEstado(response.data);
  }

  async obterCidadePorId(id: number): Promise<Cidade> {
    const response = await axiosInstance.get(API_ENDPOINTS.cidadePorID(id), {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    return this.mapCidade(response.data)
  }


  private mapEstado(data: any): Estado {
    return {
      id: data.id,
      nome: data.nome,
      uf: data.uf,
      regiao: data.regiao ? mapRegiao(data.regiao) : null,
    };
  }

  private mapCidade(data: any): Cidade {
    return {
      id: data.id,
      nome: data.nome,
      estado: data.estado ? this.mapEstado(data.estado) : null,
    };
  }
}
