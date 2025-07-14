import { Regiao } from "./regiao"
import { Estado } from "./estado"
import { User } from "./user" 
import { Cidade } from "./cidade"

export interface ApiResponse {
  success: boolean
  message: string
  data?: any
  error?: string
}

export interface Project {
  id: string;
  nome: string;
  descricao: string;
  criadoPor: string;
  atualizadoPor: string | null;
  ehRemoto: boolean;
  formato: string;
  status: string;
  vagas: number;
  ativo: boolean;
  inicioInscricoes: string;
  fimInscricoes: string;
  dataInicio: string;
  dataFim: string;
  criadoEm: string;
  atualizadoEm: string;
  regioesAceitas: Regiao[];
  estadosAceitos: Estado[];
  cidadesAceitas: Cidade[];
  regiao: Regiao | null;
  estado: Estado | null;
  cidade: Cidade | null;
  regiaoID?: number
  estadoID?: number
  cidadeID?: number
  tutorID?: string
  instituicao: string;
  tutor?: User | null;
}

export interface ProjectPayload {
  nome: string;
  descricao: string;
  eh_remoto: boolean;
  vagas: number;
  data_inicio: string;
  data_fim: string;
  inicio_inscricoes: string;
  fim_inscricoes: string;
  regioes_aceitas: string;
  formato: string;
  tutora: string;
  estados_aceitos?: string;
  cidades_aceitas?: string;
}

// export interface ProjectListItem {
//   id: string
//   nome: string
//   dataInicio: string
//   dataFim: string
//   inicioInscricoes: string
//   fimInscricoes: string
//   tutorId: string
//   tutorNome: string
//   estado: Estado
//   estadoNome: string
//   cidade: Cidade
//   formato: string
//   instituicao: string
//   vagas: number
//   regioesAceitas: string[]
//   descricao: string,
//   ativo: boolean,
//   atualizado_em?: string
//   criado_em?: string
//   criado_por?: string
//   atualizado_por?: string
//   cidades_aceitas_obj: string[]  
// }

export interface FiltrosProjects {
  titulo?: string
  tutorId?: string
  regiao?: string
  estado?: string
  cidade?: string
  formato?: string
  instituicao?: string
  dataInicio?: string
  dataFim?: string
}
