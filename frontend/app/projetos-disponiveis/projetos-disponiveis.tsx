"use client"

import { useState, useMemo } from "react"
import { Search, Calendar, Filter } from "lucide-react"
import styles from "./projetosdisponiveis.module.css"

export function ProjetosDisponiveis() {
  const [searchTerm, setSearchTerm] = useState("")
  const [startDateFilter, setStartDateFilter] = useState("")
  const [endDateFilter, setEndDateFilter] = useState("")

  // Dados mockados dos projetos
  const projects = [
    {
      id: 1,
      title: "Projeto 1",
      description:
        "Descrição projeto 1. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
      area: "Biologia",
      coordinator: "Maria Silva",
      duration: "6 meses",
      startDate: "2024-02-15",
      endDate: "2024-08-15",
      vacancies: 8,
      requirements: ["Ensino Médio em andamento", "Interesse em Biologia", "Disponibilidade de 20h semanais"],
      status: "Inscrições Abertas",
    },
    {
      id: 2,
      title: "Projeto 2",
      description:
        "Descrição Projeto 2. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
      area: "Química",
      coordinator: "João Santos",
      duration: "8 meses",
      startDate: "2024-03-01",
      endDate: "2024-11-01",
      vacancies: 6,
      requirements: ["Ensino Médio em andamento", "Bom desempenho em Química", "Interesse em sustentabilidade"],
      status: "Inscrições Abertas",
    },
    {
      id: 3,
      title: "Projeto 3",
      description:
        "Descrição Projeto 3. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
      area: "Física",
      coordinator: "Ana Costa",
      duration: "7 meses",
      startDate: "2024-01-20",
      endDate: "2024-08-20",
      vacancies: 5,
      requirements: ["Ensino Médio em andamento", "Conhecimentos básicos de Física", "Interesse em tecnologia"],
      status: "Em Andamento",
    }
  ]

  // Filtrar projetos baseado nos critérios
  const filteredProjects = useMemo(() => {
    return projects.filter((project) => {
      const matchesSearch =
        project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project.area.toLowerCase().includes(searchTerm.toLowerCase())

      const matchesStartDate = !startDateFilter || new Date(project.startDate) >= new Date(startDateFilter)
      const matchesEndDate = !endDateFilter || new Date(project.endDate) <= new Date(endDateFilter)

      return matchesSearch && matchesStartDate && matchesEndDate
    })
  }, [searchTerm, startDateFilter, endDateFilter, projects])

  const clearFilters = () => {
    setSearchTerm("")
    setStartDateFilter("")
    setEndDateFilter("")
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Inscrições Abertas":
        return styles.statusOpen
      case "Em Andamento":
        return styles.statusRunning
      case "Inscrições em Breve":
        return styles.statusSoon
      default:
        return styles.statusDefault
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Projetos Disponíveis</h1>
        <p className={styles.subtitle}>Explore os projetos de pesquisa disponíveis no programa Futuras Cientistas</p>
      </div>

      {/* Filtros */}
      <div className={styles.filtersCard}>
        <div className={styles.filtersHeader}>
          <div className={styles.filtersTitle}>
            <Filter size={20} />
            <span>Filtros</span>
          </div>
          <button onClick={clearFilters} className={styles.clearButton}>
            Limpar filtros
          </button>
        </div>

        <div className={styles.filtersContent}>
          <div className={styles.searchGroup}>
            <div className={styles.searchContainer}>
              <Search className={styles.searchIcon} size={16} />
              <input
                type="text"
                placeholder="Buscar por nome ou descrição do projeto..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className={styles.searchInput}
              />
            </div>
          </div>

          <div className={styles.dateFilters}>
            <div className={styles.dateGroup}>
              <label className={styles.dateLabel}>
                <Calendar size={16} />
                Data de início (a partir de):
              </label>
              <input
                type="date"
                value={startDateFilter}
                onChange={(e) => setStartDateFilter(e.target.value)}
                className={styles.dateInput}
              />
            </div>

            <div className={styles.dateGroup}>
              <label className={styles.dateLabel}>
                <Calendar size={16} />
                Data de fim (até):
              </label>
              <input
                type="date"
                value={endDateFilter}
                onChange={(e) => setEndDateFilter(e.target.value)}
                className={styles.dateInput}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Resultados */}
      <div className={styles.resultsHeader}>
        <span className={styles.resultsCount}>
          {filteredProjects.length} projeto{filteredProjects.length !== 1 ? "s" : ""} encontrado
          {filteredProjects.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Lista de Projetos */}
      <div className={styles.projectsList}>
        {filteredProjects.map((project) => (
          <div key={project.id} className={styles.projectCard}>
            <div className={styles.projectHeader}>
              <div className={styles.projectTitleArea}>
                <h3 className={styles.projectTitle}>{project.title}</h3>
                <span className={styles.projectArea}>{project.area}</span>
              </div>
              <span className={`${styles.projectStatus} ${getStatusColor(project.status)}`}>{project.status}</span>
            </div>

            <p className={styles.projectDescription}>{project.description}</p>

            <div className={styles.projectDetails}>
              {/* <div className={styles.detailItem}>
                <strong>Tutor:</strong> {project.coordinator}
              </div> */}
              <div className={styles.detailItem}>
                <strong>Duração:</strong> {project.duration}
              </div>
              <div className={styles.detailItem}>
                <strong>Período:</strong> {new Date(project.startDate).toLocaleDateString("pt-BR")} até{" "}
                {new Date(project.endDate).toLocaleDateString("pt-BR")}
              </div>
              <div className={styles.detailItem}>
                <strong>Vagas:</strong> {project.vacancies}
              </div>
            </div>

            {/* <div className={styles.requirements}>
              <strong>Requisitos:</strong>
              <ul className={styles.requirementsList}>
                {project.requirements.map((req, index) => (
                  <li key={index}>{req}</li>
                ))}
              </ul>
            </div> */}
          </div>
        ))}
      </div>

      {filteredProjects.length === 0 && (
        <div className={styles.noResults}>
          <p>Nenhum projeto encontrado com os filtros aplicados.</p>
          <button onClick={clearFilters} className={styles.clearButton}>
            Limpar filtros
          </button>
        </div>
      )}
    </div>
  )
}
