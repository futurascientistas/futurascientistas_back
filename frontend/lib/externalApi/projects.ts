import axiosInstance from "@/lib/axios";
import { Cidade } from "@/types/cidade";
import { Estado } from "@/types/estado";
import { Project, ProjectPayload } from "@/types/project";
import { Regiao } from "@/types/regiao";
import { EstadoApiAdapter } from "./estados"
import API_ENDPOINTS from "./endpoints";

export class ProjectApiAdapter {
  constructor(private token: string) {}

  async listarProjetos(): Promise<Project[]> {
    const res = await axiosInstance.get(API_ENDPOINTS.PROJETOS_TODOS, {
      headers: { Authorization: `Bearer ${this.token}` },
    });
    return res.data.map(this.mapProject);
  }

  async criarProjeto(projeto: Project): Promise<Project> {
    // dafault values
    projeto.formato = projeto.formato.toLowerCase() || "presencial";
    projeto.ehRemoto = projeto.ehRemoto || false;
    projeto.regioesAceitas = projeto.regioesAceitas || [];
    
    var regioes_aceitas = "";
    if(projeto.formato == 'remoto') {
      regioes_aceitas = "1,2,3,4,5"
    } else {
      regioes_aceitas = projeto.regiao.id.toString();
    }
    
    var inicio_inscricoes = projeto.inicioInscricoes;
    var fim_inscricoes = projeto.fimInscricoes;
    var cidades_aceitas = projeto.cidade ? projeto.cidade.id.toString() : "";
    var estados_aceitos = projeto.estado ? projeto.estado.id.toString() : "";
    var tutora_id = projeto.tutor ? projeto.tutor.id.toString() : "";

    const payload: ProjectPayload = {
      "nome": projeto.nome,
      "descricao": projeto.descricao,
      "eh_remoto": projeto.ehRemoto,
      "vagas": projeto.vagas,
      "data_inicio": projeto.dataInicio,
      "data_fim": projeto.dataFim,
      "inicio_inscricoes": inicio_inscricoes,
      "fim_inscricoes": fim_inscricoes,
      "regioes_aceitas": regioes_aceitas,
      "formato": projeto.formato,
      "tutora": tutora_id,
      "cidades_aceitas": cidades_aceitas,
      "estados_aceitos": estados_aceitos,
    };

    console.log("Project payload: ", payload)

    const res = await axiosInstance.post(API_ENDPOINTS.PROJETOS_CRIAR, payload, {
      headers: { Authorization: `Bearer ${this.token}` },
    });
    return this.mapProject(res.data);
  }

  private mapProject(data: any): Project {
    // var tutor
    // const estadoAdapter = new EstadoApiAdapter(this.token);
    // const estado = await estadoAdapter.obterEstadoPorId(data.estado.id)
    var estado = data.estados_aceitos_obj[0];
    var cidade = data.cidades_aceitas_obj[0];
    var regiao = data.regioes_aceitas_obj[0];
    var tutor = data.tutora;

    return {
      id: data.id,
      nome: data.nome,
      descricao: data.descricao,
      criadoPor: data.criado_por,
      atualizadoPor: data.atualizado_por,
      ehRemoto: data.eh_remoto,
      formato: data.formato,
      status: data.status,
      vagas: data.vagas,
      ativo: data.ativo,
      inicioInscricoes: data.inicio_inscricoes,
      fimInscricoes: data.fim_inscricoes,
      dataInicio: data.data_inicio,
      dataFim: data.data_fim,
      criadoEm: data.criado_em,
      atualizadoEm: data.atualizado_em,
      tutor: data.tutora,
      regioesAceitas: data.regioes_aceitas_obj.map(
        (nome: string): Regiao => ({
          nome,
          id: 0,
          abreviacao: "",
          descricao: "",
        })
      ),
      estadosAceitos: data.estados_aceitos_obj.map(
        (estado: any): Estado => ({
          id: estado.id,
          nome: estado.nome,
          uf: "",
          regiao: estado.regiao,
        })
      ),
      cidadesAceitas: data.cidades_aceitas_obj.map(
        (cidade: any): Cidade => ({
          id: cidade.id,
          nome: cidade.nome,
          estado: cidade.estado,
        })
      ),
      regiaoID: regiao,
      estadoID: estado,
      cidadeID: cidade,
      tutorID: tutor,
      instituicao: "",
    };
  }

  // static async listarProjects(): Promise<Project[]> {
  //   const response = await axios.get('/projetos/todos/');
  //   return response.data;
  // }

  // static async filtrarProjects(filtros: any): Promise<Project[]> {
  //   const response = await axios.post('/projetos/filtro/', filtros);
  //   return response.data;
  // }

  // static async criarProject(projeto: Project): Promise<Project> {
  //   const response = await axios.post('/projetos/criar/', projeto);
  //   return response.data;
  // }

  // static async getProjectById(id: string): Promise<Project> {
  //   const response = await axios.get(`/projetos/${id}/`);

  // }

  // static async buscarProjetosExternos(token: string) {
  //   const res = await axios.get('/projetos/todos/', { headers: { Authorization: `Bearer ${token}` } });
  //   return res.data;
  // }

  // static async criarProjetoExterno(token: string, projeto: Project) {
  //   const res = await axios.post('/projetos/criar/', projeto, { headers: { Authorization: `Bearer ${token}` } });
  //   return res.data;
  // }
}
