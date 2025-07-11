export interface Regiao {
  id: number
  nome: string
  abreviacao: string
  descricao: string
}

export interface RegiaoApiResponse {
  success: boolean
  message: string
  data?: Regiao[]
  error?: string
}