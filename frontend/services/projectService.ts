import axios from "lib/axios";
import type {
  ProjectFormData,
  ProjectListItem,
  ProjectPayload,
  ApiResponse,
} from "../types/project";

export class ProjectService {
  private static async makeRequest(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse> {
    try {
      const response = await fetch(`${endpoint}`, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();

      console.log("Response data:", data);

      if (!response.ok) {
        return {
          success: false,
          message: data.message || "Erro na requisição",
          error: data.error || `HTTP ${response.status}`,
        };
      }

      return {
        success: true,
        message: data.message || "Operação realizada com sucesso",
        data: data,
      };
    } catch (error) {
      console.error("Erro na requisição:", error);
      return {
        success: false,
        message: "Erro de conexão com o servidor",
        error: error instanceof Error ? error.message : "Erro desconhecido",
      };
    }
  }

  static transformFormDataToPayload(formData: ProjectFormData): ProjectPayload {
    return {
      nome: formData.titulo,
      descricao: formData.descricao,
      eh_remoto: formData.formato.toLowerCase() === "remoto",
      vagas: formData.vagas,
      data_inicio: formData.dataInicio,
      data_fim: formData.dataFim,
      inicio_inscricoes: formData.inicioInscricoes,
      fim_inscricoes: formData.fimInscricoes,
      regioes_aceitas: formData.regioesAceitas.join(","),
      formato: formData.formato.toLowerCase(),
      tutora_id: formData.tutor.id,
    };
  }

  static async criarProject(formData: ProjectFormData): Promise<ApiResponse> {
    const payload = this.transformFormDataToPayload(formData);

    return this.makeRequest("/api/projetos/criar/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async getProjectById(id: string): Promise<ProjectListItem> {
    console.log('TESTE: ' + id)
    const res = await axios.get(`/projetos/todos/?id=${id}`); // rota relativa à /api
    console.log(res)
    return res.data;
  }

  static async listarProjects(): Promise<ApiResponse> {
    const result = await this.makeRequest("/api/projetos/todos/", {
      method: "GET"      
    });

    return result;
  }

  static async filtrarProjects(filtros: any): Promise<ApiResponse> {
    const response = await this.listarProjects();

    if (!response.success || !response.data) {
      return response;
    }

    let projetosFiltrados = response.data;

    // Aplicar filtros
    if (filtros.titulo) {
      projetosFiltrados = projetosFiltrados.filter((projeto: any) =>
        projeto.titulo.toLowerCase().includes(filtros.titulo.toLowerCase())
      );
    }

    if (filtros.tutorId) {
      projetosFiltrados = projetosFiltrados.filter(
        (projeto: any) => projeto.tutorId === filtros.tutorId
      );
    }

    if (filtros.estado) {
      projetosFiltrados = projetosFiltrados.filter(
        (projeto: any) => projeto.estado === filtros.estado
      );
    }

    if (filtros.cidade) {
      projetosFiltrados = projetosFiltrados.filter((projeto: any) =>
        projeto.cidade.toLowerCase().includes(filtros.cidade.toLowerCase())
      );
    }

    if (filtros.modalidade) {
      projetosFiltrados = projetosFiltrados.filter(
        (projeto: any) => projeto.modalidade === filtros.modalidade
      );
    }

    if (filtros.instituicao) {
      projetosFiltrados = projetosFiltrados.filter((projeto: any) =>
        projeto.instituicao
          .toLowerCase()
          .includes(filtros.instituicao.toLowerCase())
      );
    }

    if (filtros.dataInicio) {
      projetosFiltrados = projetosFiltrados.filter(
        (projeto: any) =>
          new Date(projeto.dataInicio) >= new Date(filtros.dataInicio)
      );
    }

    if (filtros.dataFim) {
      projetosFiltrados = projetosFiltrados.filter(
        (projeto: any) => new Date(projeto.dataFim) <= new Date(filtros.dataFim)
      );
    }

    return {
      success: true,
      message: `${projetosFiltrados.length} projetos encontrados`,
      data: projetosFiltrados,
    };
  }

  static async updateProjeto(id: string, dados: Partial<ProjectFormData>) {
    const res = await fetch(`/api/projetos/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(dados),
    });

    if (!res.ok) {
      throw new Error("Erro ao atualizar projeto");
    }

    return res.json();
  }

  static async getProjetoById(id: string): Promise<ApiResponse> {
    try {
      const response = await this.makeRequest(`/projetos/todos/?id=${id}`, {
        method: "GET",
      })

      if (response.success && response.data) {
        // Transformar os dados da API para o formato ProjectListItem
        const apiData = response.data

        const projectListItem: ProjectListItem = {
          id: apiData.id?.toString() || id,
          titulo: apiData.nome || apiData.titulo || "",
          dataInicio: apiData.data_inicio || apiData.dataInicio || "",
          dataFim: apiData.data_fim || apiData.dataFim || "",
          inicioInscricoes: apiData.inicio_inscricoes || apiData.inicioInscricoes || "",
          fimInscricoes: apiData.fim_inscricoes || apiData.fimInscricoes || "",
          tutorId: apiData.tutora_id?.toString() || apiData.tutorId || "",
          tutorNome: apiData.tutora_nome || apiData.tutorNome || "",
          estado: apiData.estado_id?.toString() || apiData.estado || "",
          estadoNome: apiData.estado_nome || apiData.estadoNome || "",
          cidade: apiData.cidade || "",
          formato: apiData.eh_remoto ? "Remoto" : "Presencial",
          instituicao: apiData.instituicao || "",
          vagas: apiData.vagas || 0,
          regioesAceitas:
            typeof apiData.regioes_aceitas === "string"
              ? apiData.regioes_aceitas.split(",").filter(Boolean)
              : apiData.regioesAceitas || [],
          resumo: apiData.descricao || apiData.resumo || "",
          active: apiData.active !== undefined ? apiData.active : true,
        }

        return {
          success: true,
          message: "Projeto encontrado com sucesso",
          data: projectListItem,
        }
      }

      return response
    } catch (error) {
      console.error("Erro ao buscar projeto:", error)
      return {
        success: false,
        message: "Erro ao buscar projeto",
        error: error instanceof Error ? error.message : "Erro desconhecido",
      }
    }
  }
}
