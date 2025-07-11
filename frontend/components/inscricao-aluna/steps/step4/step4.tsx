"use client"

import type React from "react"

import { useState } from "react"
import styles from "./step4.module.css"

interface Step4Props {
  onComplete: (data: any) => void
  onBack: (data: any) => void
  initialData?: any
}

export function Step4({ onComplete, onBack, initialData = {} }: Step4Props) {
  const [formData, setFormData] = useState({
    nomeEscola: "",
    tipoEnsino: "",
    cep: "",
    rua: "",
    bairro: "",
    numero: "",
    complemento: "",
    cidade: "",
    estado: "",
    telefoneEscola: "",
    telefoneResponsavelEscola: "",
    ...initialData,
  })

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const formatCEP = (value: string) => {
    const numbers = value.replace(/\D/g, "")
    if (numbers.length <= 8) {
      return numbers.replace(/(\d{5})(\d{3})/, "$1-$2")
    }
    return value
  }

  const formatPhone = (value: string) => {
    const numbers = value.replace(/\D/g, "")
    if (numbers.length <= 11) {
      return numbers.replace(/(\d{2})(\d{4,5})(\d{4})/, "($1) $2-$3")
    }
    return value
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate required fields
    const requiredFields = [
      "nomeEscola",
      "tipoEnsino",
      "cep",
      "rua",
      "bairro",
      "numero",
      "complemento",
      "cidade",
      "estado",
      "telefoneEscola",
      "telefoneResponsavelEscola",
    ]
    const missingFields = requiredFields.filter((field) => !formData[field as keyof typeof formData])

    if (missingFields.length > 0) {
      alert(`Por favor, preencha os campos obrigatórios: ${missingFields.join(", ")}`)
      return
    }

    console.log("Enviando dados da etapa 4:", formData)
    onComplete(formData)
  }

  const handleBack = () => {
    console.log("Voltando da etapa 4 com dados:", formData)
    onBack(formData)
  }

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2 className={styles.cardTitle}>Dados da Escola</h2>
      </div>
      <div className={styles.cardContent}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label htmlFor="nomeEscola" className={styles.label}>
              Nome da escola *
            </label>
            <input
              id="nomeEscola"
              type="text"
              value={formData.nomeEscola}
              onChange={(e) => handleInputChange("nomeEscola", e.target.value)}
              required
              className={styles.input}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="tipoEnsino" className={styles.label}>
              Tipo de ensino *
            </label>
            <input
              id="tipoEnsino"
              type="text"
              value={formData.tipoEnsino}
              onChange={(e) => handleInputChange("tipoEnsino", e.target.value)}
              required
              className={styles.input}
              placeholder="Regular"
            />
          </div>

          <div className={styles.gridTwo}>
            <div className={styles.formGroup}>
              <label htmlFor="cep" className={styles.label}>
                CEP *
              </label>
              <input
                id="cep"
                type="text"
                value={formData.cep}
                onChange={(e) => handleInputChange("cep", formatCEP(e.target.value))}
                required
                className={styles.input}
                placeholder="00000-000"
              />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="rua" className={styles.label}>
                Rua *
              </label>
              <input
                id="rua"
                type="text"
                value={formData.rua}
                onChange={(e) => handleInputChange("rua", e.target.value)}
                required
                className={styles.input}
              />
            </div>
          </div>

          <div className={styles.gridThree}>
            <div className={styles.formGroup}>
              <label htmlFor="bairro" className={styles.label}>
                Bairro *
              </label>
              <input
                id="bairro"
                type="text"
                value={formData.bairro}
                onChange={(e) => handleInputChange("bairro", e.target.value)}
                required
                className={styles.input}
              />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="numero" className={styles.label}>
                Número *
              </label>
              <input
                id="numero"
                type="text"
                value={formData.numero}
                onChange={(e) => handleInputChange("numero", e.target.value)}
                required
                className={styles.input}
              />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="complemento" className={styles.label}>
                Complemento *
              </label>
              <input
                id="complemento"
                type="text"
                value={formData.complemento}
                onChange={(e) => handleInputChange("complemento", e.target.value)}
                required
                className={styles.input}
              />
            </div>
          </div>

          <div className={styles.gridTwo}>
            <div className={styles.formGroup}>
              <label htmlFor="cidade" className={styles.label}>
                Cidade *
              </label>
              <input
                id="cidade"
                type="text"
                value={formData.cidade}
                onChange={(e) => handleInputChange("cidade", e.target.value)}
                required
                className={styles.input}
              />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="estado" className={styles.label}>
                Estado/UF *
              </label>
              <input
                id="estado"
                type="text"
                value={formData.estado}
                onChange={(e) => handleInputChange("estado", e.target.value)}
                required
                className={styles.input}
                maxLength={2}
                placeholder="SP"
              />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="telefoneEscola" className={styles.label}>
              Telefone da escola *
            </label>
            <input
              id="telefoneEscola"
              type="text"
              value={formData.telefoneEscola}
              onChange={(e) => handleInputChange("telefoneEscola", formatPhone(e.target.value))}
              required
              className={styles.input}
              placeholder="(11) 9999-9999"
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="telefoneResponsavelEscola" className={styles.label}>
              Telefone de um responsável pela escola *
            </label>
            <input
              id="telefoneResponsavelEscola"
              type="text"
              value={formData.telefoneResponsavelEscola}
              onChange={(e) => handleInputChange("telefoneResponsavelEscola", formatPhone(e.target.value))}
              required
              className={styles.input}
              placeholder="(11) 99999-9999"
            />
          </div>

          <div className={styles.buttonContainer}>
            <button type="button" onClick={handleBack} className={styles.backButton}>
              ← Voltar
            </button>
            <button type="submit" className={styles.submitButton}>
              Salvar e continuar →
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
