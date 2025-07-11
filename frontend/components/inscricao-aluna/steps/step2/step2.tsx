"use client"

import type React from "react"

import { useState } from "react"
import styles from "./step2.module.css"

interface Step2Props {
  onComplete: (data: any) => void
  onBack: (data: any) => void
  initialData?: any
}

export function Step2({ onComplete, onBack, initialData = {} }: Step2Props) {
  const [formData, setFormData] = useState({
    cep: "",
    rua: "",
    bairro: "",
    numero: "",
    complemento: "",
    cidade: "",
    estado: "",
    uploadComprovanteResidencia: null,
    ...initialData,
  })

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleFileChange = (field: string, file: File | null) => {
    setFormData((prev) => ({ ...prev, [field]: file }))
  }

  const formatCEP = (value: string) => {
    const numbers = value.replace(/\D/g, "")
    if (numbers.length <= 8) {
      return numbers.replace(/(\d{5})(\d{3})/, "$1-$2")
    }
    return value
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate required fields
    const requiredFields = ["cep", "rua", "bairro", "numero", "complemento", "cidade", "estado"]
    const missingFields = requiredFields.filter((field) => !formData[field as keyof typeof formData])

    if (missingFields.length > 0) {
      alert(`Por favor, preencha os campos obrigatórios: ${missingFields.join(", ")}`)
      return
    }

    console.log("Enviando dados da etapa 2:", formData)
    onComplete(formData)
  }

  const handleBack = () => {
    console.log("Voltando da etapa 2 com dados:", formData)
    onBack(formData)
  }

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2 className={styles.cardTitle}>Localização e Endereço</h2>
      </div>
      <div className={styles.cardContent}>
        <form onSubmit={handleSubmit} className={styles.form}>
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
            <label htmlFor="uploadComprovanteResidencia" className={styles.label}>
              Upload Comprovante de Residência *
            </label>
            <input
              id="uploadComprovanteResidencia"
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={(e) => handleFileChange("uploadComprovanteResidencia", e.target.files?.[0] || null)}
              required
              className={styles.fileInput}
            />
            <p className={styles.fileHint}>Selecione arquivo</p>
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
