"use client"

import { useState } from "react"
import styles from "./projectselection.module.css"

interface ProjectSelectionProps {
  onReview?: () => void
}

export function ProjectSelection({ onReview }: ProjectSelectionProps) {
  const [selectedProject, setSelectedProject] = useState("")

  const projects = [
    {
      id: "projeto-1",
      title: "Projeto 1",
      description: "Descrição Projeto 1",
      duration: "6 meses",
      area: "Biologia",
    },
    {
      id: "projeto-2",
      title: "Projeto 2",
      description: "Descrição Projeto 2",
      duration: "8 meses",
      area: "Química",
    },
    {
      id: "projeto-3",
      title: "Projeto 3",
      description: "Descrição Projeto 3",
      duration: "7 meses",
      area: "Física",
    }
  ]

  const handleSubmit = async () => {
    if (selectedProject) {
      try {
        // For development/testing, simulate success
        /*
      const response = await fetch("http://localhost:8000/inscricoes/selecionar_projeto/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          projeto_id: selectedProject,
        }),
      })

      if (!response.ok) {
        throw new Error("Erro ao selecionar projeto")
      }
      */

        console.log("Projeto selecionado:", selectedProject)
        alert("Inscrição finalizada com sucesso!")
      } catch (error) {
        console.error("Erro:", error)
        alert("Erro ao finalizar inscrição. Tente novamente.")
      }
    } else {
      alert("Por favor, selecione um projeto antes de finalizar.")
    }
  }

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h2 className={styles.cardTitle}>Seleção de Projetos de Trabalho</h2>
        <p className={styles.cardDescription}>Escolha o projeto no qual deseja participar durante o programa</p>
      </div>
      <div className={styles.cardContent}>
        <div className={styles.projectList}>
          {projects.map((project) => (
            <div key={project.id} className={styles.projectItem}>
              <input
                type="radio"
                id={project.id}
                name="project"
                value={project.id}
                checked={selectedProject === project.id}
                onChange={(e) => setSelectedProject(e.target.value)}
                className={styles.radioInput}
              />
              <div className={styles.projectContent}>
                <label htmlFor={project.id} className={styles.projectLabel}>
                  <div className={styles.projectTitle}>{project.title}</div>
                  <div className={styles.projectDescription}>{project.description}</div>
                  <div className={styles.projectMeta}>
                    {/* <span>Área: {project.area}</span> */}
                    <span>Duração: {project.duration}</span>
                  </div>
                </label>
              </div>
            </div>
          ))}
        </div>

        <div className={styles.buttonContainer}>
          {onReview && (
            <button onClick={onReview} className={styles.reviewButton}>
              Revisar dados de inscrição
            </button>
          )}
          <button
            onClick={handleSubmit}
            disabled={!selectedProject}
            className={`${styles.submitButton} ${!selectedProject ? styles.disabled : ""}`}
          >
            Finalizar Inscrição
          </button>
        </div>
      </div>
    </div>
  )
}
