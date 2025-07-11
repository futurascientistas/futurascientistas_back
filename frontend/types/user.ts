export type UserProfile = "estudante" | "admin" | "professor" | "tutor"

export interface User {
  id: string,
  name: string,
  profile: UserProfile,
  email?: string,
  perfil: string,
  cpf?: string,
}

export interface UserApiResponse {
  success: boolean
  message: string
  data?: User[]
  error?: string
}