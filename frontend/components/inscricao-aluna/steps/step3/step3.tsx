"use client"

import type React from "react"

import { useState } from "react"
import styles from "./step3.module.css"

interface Step3Props {
  onComplete: (data: any) => void
  onBack: (data: any) => void
  initialData?: any
}

export function Step3({ onComplete, onBack, initialData = {} }: Step3Props) {
  const [formData, setFormData] = useState({
    genero: "",
    generoOutro: "",
    pronomes: "",
    autodeclaracaoRacial: "",
    deficiencias: "",
    deficienciasOutro: "",
    ...initialData,
  })

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate required fields
    if (!formData.genero || !formData.pronomes || !formData.autodeclaracaoRacial || !formData.deficiencias) {
      alert("Por favor, preencha todos os campos obrigatórios")
      return
    }

    // Validate conditional fields
    if (formData.genero === "Outro" && !formData.generoOutro) {
      alert("Por favor, especifique o gênero")
      return
    }

    if (formData.deficiencias === "Outro" && !formData.deficienciasOutro) {
      alert("Por favor, especifique a deficiência")
      return
    }

    console.log("Enviando dados da etapa 3:", formData)
    onComplete(formData)
  }

  const handleBack = () => {
    console.log("Voltando da etapa 3 com dados:", formData)
    onBack(formData)
  }

  const genderOptions = [
    "Mulher cisgênero",
    "Mulher transgênero",
    "Homem cisgênero",
    "Homem transgênero",
    "Pessoa não binária",
    "Pessoa agênero",
    "Pessoa intersexo",
    "Prefere não dizer",
    "Outro",
  ]

  const raceOptions = ["Branca", "Preta", "Parda", "Amarela", "Indígena"]

  const disabilityOptions = [
    "Deficiência física",
    "Deficiência auditiva",
    "Deficiência visual",
    "Deficiência intelectual",
    "Deficiência múltipla",
    "Transtorno do espectro autista (TEA)",
    "Outro",
  ]

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2 className={styles.cardTitle}>Classificação social</h2>
      </div>
      <div className={styles.cardContent}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label htmlFor="genero" className={styles.label}>
              Gênero *
            </label>
            <select
              id="genero"
              value={formData.genero}
              onChange={(e) => handleInputChange("genero", e.target.value)}
              required
              className={styles.select}
            >
              <option value="">Selecione uma opção</option>
              {genderOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            {formData.genero === "Outro" && (
              <input
                type="text"
                placeholder="Especifique o gênero"
                value={formData.generoOutro}
                onChange={(e) => handleInputChange("generoOutro", e.target.value)}
                required
                className={`${styles.input} ${styles.conditionalInput}`}
              />
            )}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="pronomes" className={styles.label}>
              Pronomes *
            </label>
            <input
              id="pronomes"
              type="text"
              value={formData.pronomes}
              onChange={(e) => handleInputChange("pronomes", e.target.value)}
              required
              className={styles.input}
              placeholder="Ex: ela/dela, ele/dele, elu/delu"
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="autodeclaracaoRacial" className={styles.label}>
              Autodeclaração racial *
            </label>
            <select
              id="autodeclaracaoRacial"
              value={formData.autodeclaracaoRacial}
              onChange={(e) => handleInputChange("autodeclaracaoRacial", e.target.value)}
              required
              className={styles.select}
            >
              <option value="">Selecione uma opção</option>
              {raceOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="deficiencias" className={styles.label}>
              Deficiências *
            </label>
            <select
              id="deficiencias"
              value={formData.deficiencias}
              onChange={(e) => handleInputChange("deficiencias", e.target.value)}
              required
              className={styles.select}
            >
              <option value="">Selecione uma opção</option>
              {disabilityOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            {formData.deficiencias === "Outro" && (
              <input
                type="text"
                placeholder="Especifique a deficiência"
                value={formData.deficienciasOutro}
                onChange={(e) => handleInputChange("deficienciasOutro", e.target.value)}
                required
                className={`${styles.input} ${styles.conditionalInput}`}
              />
            )}
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
