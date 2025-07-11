"use client"

import type React from "react"

import { useState } from "react"
import styles from "./step5.module.css"

interface Step5Props {
  onComplete: (data: any) => void
  onBack: (data: any) => void
  initialData?: any
}

export function Step5({ onComplete, onBack, initialData = {} }: Step5Props) {
  const [grades, setGrades] = useState({
    quimica: { bimestre1: "", bimestre2: "" },
    fisica: { bimestre1: "", bimestre2: "" },
    matematica: { bimestre1: "", bimestre2: "" },
    biologia: { bimestre1: "", bimestre2: "" },
    portugues: { bimestre1: "", bimestre2: "" },
    ...(initialData.grades || {}),
  })

  const [files, setFiles] = useState({
    historicoEscolar: null,
    autorizacaoResponsavel: null,
    ...(initialData.files || {}),
  })

  const handleGradeChange = (subject: string, bimester: string, value: string) => {
    setGrades((prev) => ({
      ...prev,
      [subject]: {
        ...prev[subject as keyof typeof prev],
        [bimester]: value,
      },
    }))
  }

  const handleFileChange = (field: string, file: File | null) => {
    setFiles((prev) => ({ ...prev, [field]: file }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    // Validate grades
    const subjects = ["quimica", "fisica", "matematica", "biologia", "portugues"]
    for (const subject of subjects) {
      const subjectGrades = grades[subject as keyof typeof grades]
      if (!subjectGrades.bimestre1 || !subjectGrades.bimestre2) {
        alert(`Por favor, preencha todas as notas de ${subject}`)
        return
      }
    }

    // Validate files
    if (!files.historicoEscolar || !files.autorizacaoResponsavel) {
      alert("Por favor, faça upload de todos os documentos obrigatórios")
      return
    }

    console.log("Enviando dados da etapa 5:", { grades, files })
    onComplete({ grades, files })
  }

  const handleBack = () => {
    console.log("Voltando da etapa 5 com dados:", { grades, files })
    onBack({ grades, files })
  }

  const subjects = [
    { key: "quimica", name: "Química" },
    { key: "fisica", name: "Física" },
    { key: "matematica", name: "Matemática" },
    { key: "biologia", name: "Biologia" },
    { key: "portugues", name: "Português" },
  ]

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2 className={styles.cardTitle}>Histórico escolar</h2>
      </div>
      <div className={styles.cardContent}>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label className={styles.tableLabel}>Médias dos dois primeiros bimestres *</label>
            <div className={styles.tableContainer}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th className={styles.tableHeader}>Disciplina</th>
                    <th className={styles.tableHeader}>1º Bimestre</th>
                    <th className={styles.tableHeader}>2º Bimestre</th>
                  </tr>
                </thead>
                <tbody>
                  {subjects.map((subject) => (
                    <tr key={subject.key}>
                      <td className={styles.tableCell}>{subject.name}</td>
                      <td className={styles.tableCell}>
                        <input
                          type="text"
                          value={grades[subject.key as keyof typeof grades].bimestre1}
                          onChange={(e) => handleGradeChange(subject.key, "bimestre1", e.target.value)}
                          required
                          placeholder=""
                          className={styles.gradeInput}
                        />
                      </td>
                      <td className={styles.tableCell}>
                        <input
                          type="text"
                          value={grades[subject.key as keyof typeof grades].bimestre2}
                          onChange={(e) => handleGradeChange(subject.key, "bimestre2", e.target.value)}
                          required
                          placeholder=""
                          className={styles.gradeInput}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="historicoEscolar" className={styles.label}>
              Upload do histórico escolar *
            </label>
            <input
              id="historicoEscolar"
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={(e) => handleFileChange("historicoEscolar", e.target.files?.[0] || null)}
              required
              className={styles.fileInput}
            />
            <p className={styles.fileHint}>Arquivo comprobatório do boletim escolar</p>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="autorizacaoResponsavel" className={styles.label}>
              Upload da autorização do responsável *
            </label>
            <input
              id="autorizacaoResponsavel"
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={(e) => handleFileChange("autorizacaoResponsavel", e.target.files?.[0] || null)}
              required
              className={styles.fileInput}
            />
            <p className={styles.fileHint}>Arquivo com a autorização assinada pelo responsável</p>
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
