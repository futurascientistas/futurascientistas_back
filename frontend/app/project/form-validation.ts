import type { Project } from "@/types/project"

export interface ValidationError {
  field: string
  message: string
}

export class FormValidator {
  static validateProject(data: Project): ValidationError[] {
    const errors: ValidationError[] = []

    // Validações obrigatórias
    if (!data.nome.trim()) {
      errors.push({ field: "nome", message: "Nome é obrigatório" })
    }

    if (!data.descricao.trim()) {
      errors.push({ field: "descricao", message: "Resumo é obrigatório" })
    }

    if (!data.formato.trim()) {
      errors.push({ field: "formato", message: "Formato é obrigatório" })
    }

    if (!data.instituicao.trim()) {
      errors.push({ field: "instituicao", message: "Instituição é obrigatória" })
    }

    if (data.formato.trim().toLowerCase() == 'presencial' && !data.regiao) {
      errors.push({ field: "regiao", message: "Região é obrigatória" })
    }

    if (data.formato.trim().toLowerCase() == 'presencial' && !data.estado) {
      errors.push({ field: "estado", message: "Estado é obrigatório" })
    }

    if (data.formato.trim().toLowerCase() == 'presencial' && !data.cidade) {
      errors.push({ field: "cidade", message: "Cidade é obrigatória" })
    }

    if (!data.tutor) {
      errors.push({ field: "tutor", message: "Tutor é obrigatório" })
    }

    if (data.vagas <= 0) {
      errors.push({ field: "vagas", message: "Número de vagas deve ser maior que zero" })
    }

    if (!data.dataInicio) {
      errors.push({ field: "dataInicio", message: "Data de início é obrigatória" })
    }

    if (!data.dataFim) {
      errors.push({ field: "dataFim", message: "Data de fim é obrigatória" })
    }

    if (!data.inicioInscricoes) {
      errors.push({ field: "inicioInscricoes", message: "Início das inscrições é obrigatório" })
    }

    if (!data.fimInscricoes) {
      errors.push({ field: "fimInscricoes", message: "Fim das inscrições é obrigatório" })
    }

    if (data.formato.trim() == 'presencial' && data.regioesAceitas.length === 0) {
      errors.push({ field: "regioesAceitas", message: "Selecione pelo menos uma região" })
    }

    // Validações de datas
    const hoje = new Date()
    hoje.setHours(0, 0, 0, 0)

    if (data.dataInicio) {
      const dataInicio = new Date(data.dataInicio)
      if (dataInicio < hoje) {
        errors.push({ field: "dataInicio", message: "Data de início não pode ser no passado" })
      }
    }

    if (data.dataFim) {
      const dataFim = new Date(data.dataFim)
      if (dataFim < hoje) {
        errors.push({ field: "dataFim", message: "Data de fim não pode ser no passado" })
      }
    }

    if (data.dataInicio && data.dataFim) {
      const inicio = new Date(data.dataInicio)
      const fim = new Date(data.dataFim)

      if (fim <= inicio) {
        errors.push({ field: "dataFim", message: "Data de fim deve ser posterior à data de início" })
      }
    }

    if (data.inicioInscricoes && data.fimInscricoes) {
      const inicioInsc = new Date(data.inicioInscricoes)
      const fimInsc = new Date(data.fimInscricoes)

      if (fimInsc <= inicioInsc) {
        errors.push({ field: "fimInscricoes", message: "Fim das inscrições deve ser posterior ao início" })
      }
    }

    if (data.inicioInscricoes && data.dataInicio) {
      const inicioInsc = new Date(data.inicioInscricoes)
      const inicioProj = new Date(data.dataInicio)

      if (inicioInsc >= inicioProj) {
        errors.push({ field: "inicioInscricoes", message: "Inscrições devem começar antes do projeto" })
      }
    }

    return errors
  }

  static getFieldError(errors: ValidationError[], fieldName: string): string | undefined {
    return errors.find((error) => error.field === fieldName)?.message
  }
}
