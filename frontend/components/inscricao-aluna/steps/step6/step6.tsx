"use client"

import type React from "react"

import { useState } from "react"
import styles from "./step6.module.css"

interface Step6Props {
  onComplete: (data: any) => void
  onBack: (data: any) => void
  initialData?: any
}

export function Step6({ onComplete, onBack, initialData = {} }: Step6Props) {
  const [agreed, setAgreed] = useState(initialData.declaracaoVerdadeira || false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!agreed) {
      alert("Por favor, aceite a declaração para continuar")
      return
    }

    console.log("Enviando dados da etapa 6:", { declaracaoVerdadeira: true })
    onComplete({ declaracaoVerdadeira: true })
  }

  const handleBack = () => {
    console.log("Voltando da etapa 6 com dados:", { declaracaoVerdadeira: agreed })
    onBack({ declaracaoVerdadeira: agreed })
  }

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2 className={styles.cardTitle}>Declaração de informações verdadeiras</h2>
      </div>
      <div className={styles.cardContent}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.declarationBox}>
            <p className={styles.declarationText}>Ao prosseguir com esta inscrição, você declara que:</p>
            <ul className={styles.declarationList}>
              <li>Todas as informações fornecidas são verdadeiras e corretas</li>
              <li>Os documentos enviados são autênticos e não foram alterados</li>
              <li>Está ciente de que informações falsas podem resultar no cancelamento da inscrição</li>
              <li>Autoriza o uso dos dados fornecidos para fins do processo seletivo</li>
            </ul>
          </div>

          <div className={styles.checkboxContainer}>
            <input
              type="checkbox"
              id="declaration"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              required
              className={styles.checkbox}
            />
            <label htmlFor="declaration" className={styles.checkboxLabel}>
              Declaro que todas as informações fornecidas são verdadeiras *
            </label>
          </div>

          <div className={styles.buttonContainer}>
            <button type="button" onClick={handleBack} className={styles.backButton}>
              ← Voltar
            </button>
            <button
              type="submit"
              disabled={!agreed}
              className={`${styles.submitButton} ${!agreed ? styles.disabled : ""}`}
            >
              Salvar e continuar →
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
