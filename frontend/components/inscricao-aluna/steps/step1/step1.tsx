"use client"

import type React from "react"

import { useState } from "react"
import styles from "./step1.module.css"

interface Step1Props {
  onComplete: (data: any) => void
  initialData?: any
}

export function Step1({ onComplete, initialData = {} }: Step1Props) {
  const [formData, setFormData] = useState({
    comoFicouSabendo: "",
    nomeCompleto: "Sabrina Estudante",
    dataNascimento: "",
    cpf: "700.575.930-35",
    rg: "",
    telefone: "",
    telefoneResponsavel: "",
    linkLattes: "",
    uploadCpf: null,
    uploadRg: null,
    ...initialData,
  })

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleFileChange = (field: string, file: File | null) => {
    setFormData((prev) => ({ ...prev, [field]: file }))
  }

  const formatPhone = (value: string) => {
    const numbers = value.replace(/\D/g, "")
    if (numbers.length <= 11) {
      return numbers.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3")
    }
    return value
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate required fields
    const requiredFields = [
      "comoFicouSabendo",
      "nomeCompleto",
      "dataNascimento",
      "rg",
      "telefone",
      "telefoneResponsavel",
      "linkLattes",
    ]
    const missingFields = requiredFields.filter((field) => !formData[field as keyof typeof formData])

    if (missingFields.length > 0) {
      alert(`Por favor, preencha os campos obrigatórios: ${missingFields.join(", ")}`)
      return
    }

    console.log("Enviando dados da etapa 1:", formData)
    onComplete(formData)
  }

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2 className={styles.cardTitle}>Dados pessoais</h2>
      </div>
      <div className={styles.cardContent}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label htmlFor="comoFicouSabendo" className={styles.label}>
              Como ficou sabendo do programa? *
            </label>
            <input
              id="comoFicouSabendo"
              value={formData.comoFicouSabendo}
              onChange={(e) => handleInputChange("comoFicouSabendo", e.target.value)}
              required
              className={styles.input}
              placeholder="Descreva brevemente como conheceu o programa"
              // rows={3}
            />
          </div>

          <div className={styles.gridTwo}>
            <div className={styles.formGroup}>
              <label htmlFor="nomeCompleto" className={styles.label}>
                Nome completo *
              </label>
              <input
                id="nomeCompleto"
                type="text"
                value={formData.nomeCompleto}
                onChange={(e) => handleInputChange("nomeCompleto", e.target.value)}
                required
                disabled
                className={`${styles.input} ${styles.disabled}`}
              />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="dataNascimento" className={styles.label}>
                Data de Nascimento *
              </label>
              <input
                id="dataNascimento"
                type="date"
                value={formData.dataNascimento}
                onChange={(e) => handleInputChange("dataNascimento", e.target.value)}
                required
                className={styles.input}
              />
            </div>
          </div>

          <div className={styles.gridTwo}>
            <div className={styles.formGroup}>
              <label htmlFor="cpf" className={styles.label}>
                CPF *
              </label>
              <input
                id="cpf"
                type="text"
                value={formData.cpf}
                disabled
                className={`${styles.input} ${styles.disabled}`}
              />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="rg" className={styles.label}>
                RG *
              </label>
              <input
                id="rg"
                type="text"
                value={formData.rg}
                onChange={(e) => handleInputChange("rg", e.target.value)}
                required
                className={styles.input}
              />
            </div>
          </div>

          <div className={styles.gridTwo}>
            <div className={styles.formGroup}>
              <label htmlFor="telefone" className={styles.label}>
                Telefone *
              </label>
              <input
                id="telefone"
                type="text"
                value={formData.telefone}
                onChange={(e) => handleInputChange("telefone", formatPhone(e.target.value))}
                required
                className={styles.input}
                placeholder="(11) 99999-9999"
              />
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="telefoneResponsavel" className={styles.label}>
                Telefone do responsável *
              </label>
              <input
                id="telefoneResponsavel"
                type="text"
                value={formData.telefoneResponsavel}
                onChange={(e) => handleInputChange("telefoneResponsavel", formatPhone(e.target.value))}
                required
                className={styles.input}
                placeholder="(11) 99999-9999"
              />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="linkLattes" className={styles.label}>
              Link do Lattes *
            </label>
            <input
              id="linkLattes"
              type="url"
              value={formData.linkLattes}
              onChange={(e) => handleInputChange("linkLattes", e.target.value)}
              required
              className={styles.input}
              placeholder="http://lattes.cnpq.br/..."
            />
          </div>

          <div className={styles.gridTwo}>
            <div className={styles.formGroup}>
              <label htmlFor="uploadCpf" className={styles.label}>
                Upload CPF *
              </label>
              <input
                id="uploadCpf"
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => handleFileChange("uploadCpf", e.target.files?.[0] || null)}
                required
                className={styles.fileInput}
              />
              <p className={styles.fileHint}>Selecione arquivo</p>
            </div>
            <div className={styles.formGroup}>
              <label htmlFor="uploadRg" className={styles.label}>
                Upload RG *
              </label>
              <input
                id="uploadRg"
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => handleFileChange("uploadRg", e.target.files?.[0] || null)}
                required
                className={styles.fileInput}
              />
              <p className={styles.fileHint}>Selecione arquivo</p>
            </div>
          </div>

          <div className={styles.buttonContainer}>
            <button type="submit" className={styles.submitButton}>
              Salvar e continuar →
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
