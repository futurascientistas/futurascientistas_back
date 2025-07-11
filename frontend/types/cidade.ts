import { Estado } from "./estado"

export interface Cidade {
  id: number
  nome: string
  estado: Estado
}

export interface CidadeApiResponse {
  success: boolean
  message: string
  data?: Cidade[]
  error?: string
}