import { Regiao } from "./regiao"
export interface Estado {
  id: number
  nome: string
  uf: string
  regiao: Regiao
}
export interface EstadoApiResponse {
  success: boolean
  message: string
  data?: Estado[]
  error?: string
}