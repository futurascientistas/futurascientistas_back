"use client";

import React from "react"
import { useState } from "react";
import {
  Search,
  Filter,
  X,
  Calendar,
  User,
  MapPin,
  Building,
  Edit,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import styles from "./projectlist.module.css";
import { useProjects } from "@/hooks/projects/use-projects";
import { useEstados } from "@/hooks/use-estados";
import { useUsers } from "@/hooks/use-users";
import type { FiltrosProjects, Project } from "@/types/project";
import ModalDetalhesProjeto from "./modal-project-details/modal-project-detail";
import { useRouter } from "next/navigation";

type SortField = "nome" | "dataInicio" | "dataFim" | "tutor" | "regiao" | "estado" | "cidade" | "formato" | "vagas"
type SortDirection = "asc" | "desc"

export default function ProjectList() {
  const router = useRouter();

  const [mostrarFiltros, setMostrarFiltros] = useState(false);
  const [filtrosLocais, setFiltrosLocais] = useState<FiltrosProjects>({});
  const [projetoSelecionado, setProjetoSelecionado] = useState<Project | null>(null);
  const [modalAberto, setModalAberto] = useState(false);
  const [projetoEmEdicao, setProjetoEmEdicao] = useState<Project | null>(null);
  const [modoEdicao, setModoEdicao] = useState(false);

  // Sort control
  const [sortField, setSortField] = useState<SortField | null>(null)
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc")

  const {
    projetos,
    isLoading,
    error,
    aplicarFiltros,
    limparFiltros,
    totalProjetos,
    projetosFiltrados,
  } = useProjects();
  const { estados } = useEstados();
  // const { tutores } = useUsers('tutor');

  const formatos = ["Presencial", "Remoto"];

  const handleFiltroChange = (campo: keyof FiltrosProjects, valor: string) => {
    setFiltrosLocais((prev) => ({
      ...prev,
      [campo]: valor || undefined,
    }));
  };

  const handleAplicarFiltros = () => {
    aplicarFiltros(filtrosLocais);
    setMostrarFiltros(false);
  };

  const handleLimparFiltros = () => {
    setFiltrosLocais({});
    limparFiltros();
    setMostrarFiltros(false);
  };

  const formatarData = (data: string) => {
    return new Date(data).toLocaleDateString("pt-BR");
  };

  // const getTutorNome = (tutorId: string) => {
  //   const tutor = tutores.find((t) => t.id === tutorId);
  //   return tutor ? tutor.nome : tutorId;
  // };

  const temFiltrosAtivos = Object.values(filtrosLocais).some(
    (valor) => valor && valor.trim() !== ""
  );

  const handleRowClick = (projeto: Project) => {
    setProjetoSelecionado(projeto);
    setModalAberto(true);
  };

  const handleCloseModal = () => {
    setModalAberto(false);
    setProjetoSelecionado(null);
  };

  const handleEditProject = (projeto: Project) => {
    setProjetoEmEdicao(projeto);
    setModoEdicao(true);

    // Fechar o modal de detalhes
    handleCloseModal();
    router.push(`/project-edit/${projeto.id}`);
  };

  const handleEditClick = (e: React.MouseEvent, projeto: Project) => {
    e.stopPropagation();
    handleEditProject(projeto);
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Se já está ordenando por este campo, inverte a direção
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      // Se é um novo campo, começa com ascendente
      setSortField(field)
      setSortDirection("asc")
    }
  }

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return null
    }
    return sortDirection === "asc" ? (
      <ChevronUp size={14} className={styles.sortIcon} />
    ) : (
      <ChevronDown size={14} className={styles.sortIcon} />
    )
  }

  const sortedProjetos = React.useMemo(() => {
    if (!sortField) return projetos

    console.log("List projects", projetos)

    return [...projetos].sort((a, b) => {
      let aValue: string | number
      let bValue: string | number

      switch (sortField) {
        case "nome":
          aValue = a.nome.toLowerCase()
          bValue = b.nome.toLowerCase()
          break
        case "dataInicio":
          aValue = new Date(a.dataInicio).getTime()
          bValue = new Date(b.dataInicio).getTime()
          break
        case "dataFim":
          aValue = new Date(a.dataFim).getTime()
          bValue = new Date(b.dataFim).getTime()
          break
        case "tutor":
          aValue = a.tutor.name.toLowerCase()
          bValue = b.tutor.name.toLowerCase()
          break
        case "regiao":
          aValue = a.regiao.nome.toLowerCase()
          bValue = b.regiao.nome.toLowerCase()
          break
        case "estado":
          aValue = a.estado.nome.toLowerCase()
          bValue = b.estado.nome.toLowerCase()
          break
        case "cidade":
          aValue = a.cidade.nome.toLowerCase()
          bValue = b.cidade.nome.toLowerCase()
          break
        case "formato":
          aValue = a.formato.toLowerCase()
          bValue = b.formato.toLowerCase()
          break
        case "vagas":
          aValue = a.vagas
          bValue = b.vagas
          break
        default:
          return 0
      }

      if (typeof aValue === "string" && typeof bValue === "string") {
        const comparison = aValue.localeCompare(bValue)
        return sortDirection === "asc" ? comparison : -comparison
      } else {
        const comparison = (aValue as number) - (bValue as number)
        return sortDirection === "asc" ? comparison : -comparison
      }
    })
  }, [projetos, sortField, sortDirection])

  return (
    <div>
      {/* Header da página */}
      <div className={styles.pageHeader}>
        <div>
          <h1 className={styles.pageTitle}>Lista de Projetos</h1>
          <p className={styles.pageSubtitle}>
            {isLoading
              ? "Carregando projetos..."
              : `${projetosFiltrados} de ${totalProjetos} projetos encontrados`}
          </p>
        </div>
        <button
          type="button"
          onClick={() => setMostrarFiltros(!mostrarFiltros)}
          className={`${styles.filterButton} ${
            mostrarFiltros ? styles.filterButtonActive : ""
          }`}
        >
          <Filter size={16} />
          Filtros
          {temFiltrosAtivos && <span className={styles.filterBadge}></span>}
        </button>
      </div>

      {/* Painel de Filtros */}
      {mostrarFiltros && (
        <div className={styles.filterPanel}>
          <div className={styles.filterHeader}>
            <h3 className={styles.filterTitle}>
              <Filter size={16} />
              Filtrar Projetos
            </h3>
            <button
              type="button"
              onClick={() => setMostrarFiltros(false)}
              className={styles.closeButton}
              aria-label="Fechar filtros"
            >
              <X size={16} />
            </button>
          </div>

          <div className={styles.filterContent}>
            <div className={styles.filterGrid}>
              {/* Título */}
              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <Search size={14} />
                  Título do Projeto
                </label>
                <input
                  type="text"
                  value={filtrosLocais.titulo || ""}
                  onChange={(e) => handleFiltroChange("titulo", e.target.value)}
                  className={styles.filterInput}
                  placeholder="Buscar por título..."
                />
              </div>

              {/* Tutor */}
              {/* <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <User size={14} />
                  Tutor
                </label>
                <select
                  value={filtrosLocais.tutorId || ""}
                  onChange={(e) =>
                    handleFiltroChange("tutorId", e.target.value)
                  }
                  className={styles.filterSelect}
                >
                  <option value="">Todos os tutores</option>
                  {tutores.map((tutor) => (
                    <option key={tutor.id} value={tutor.id}>
                      {tutor.nome}
                    </option>
                  ))}
                </select>
              </div> */}

              {/* Estado */}
              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <MapPin size={14} />
                  Estado
                </label>
                <select
                  value={filtrosLocais.estado || ""}
                  onChange={(e) => handleFiltroChange("estado", e.target.value)}
                  className={styles.filterSelect}
                >
                  <option value="">Todos os estados</option>
                  {estados.map((estado) => (
                    <option key={estado.id} value={estado.id}>
                      {estado.nome}
                    </option>
                  ))}
                </select>
              </div>

              {/* Cidade */}
              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <MapPin size={14} />
                  Cidade
                </label>
                <input
                  type="text"
                  value={filtrosLocais.cidade || ""}
                  onChange={(e) => handleFiltroChange("cidade", e.target.value)}
                  className={styles.filterInput}
                  placeholder="Buscar por cidade..."
                />
              </div>

              {/* Modalidade */}
              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>Formato</label>
                <select
                  value={filtrosLocais.formato || ""}
                  onChange={(e) =>
                    handleFiltroChange("formato", e.target.value)
                  }
                  className={styles.filterSelect}
                >
                  <option value="">Todos os formatos</option>
                  {formatos.map((formato) => (
                    <option key={formato} value={formato}>
                      {formato}
                    </option>
                  ))}
                </select>
              </div>

              {/* Instituição */}
              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <Building size={14} />
                  Instituição
                </label>
                <input
                  type="text"
                  value={filtrosLocais.instituicao || ""}
                  onChange={(e) =>
                    handleFiltroChange("instituicao", e.target.value)
                  }
                  className={styles.filterInput}
                  placeholder="Buscar por instituição..."
                />
              </div>

              {/* Data Início */}
              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <Calendar size={14} />
                  Data Início (a partir de)
                </label>
                <input
                  type="date"
                  value={filtrosLocais.dataInicio || ""}
                  onChange={(e) =>
                    handleFiltroChange("dataInicio", e.target.value)
                  }
                  className={styles.filterInput}
                />
              </div>

              {/* Data Fim */}
              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <Calendar size={14} />
                  Data Fim (até)
                </label>
                <input
                  type="date"
                  value={filtrosLocais.dataFim || ""}
                  onChange={(e) =>
                    handleFiltroChange("dataFim", e.target.value)
                  }
                  className={styles.filterInput}
                />
              </div>
            </div>

            <div className={styles.filterActions}>
              <button
                type="button"
                onClick={handleLimparFiltros}
                className={styles.clearButton}
              >
                Limpar Filtros
              </button>
              <button
                type="button"
                onClick={handleAplicarFiltros}
                className={styles.applyButton}
              >
                Aplicar Filtros
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Mensagem de erro */}
      {error && (
        <div className={styles.errorMessage}>
          <p>{error}</p>
        </div>
      )}

      {/* Tabela de Projetos */}
      <div className={styles.tableContainer}>
        {isLoading ? (
          <div className={styles.loadingState}>
            <div className={styles.loadingSpinner}></div>
            <p>Carregando projetos...</p>
          </div>
        ) : sortedProjetos.length === 0 ? (
          <div className={styles.emptyState}>
            <Search size={48} className={styles.emptyIcon} />
            <h3>Nenhum projeto encontrado</h3>
            <p>
              Tente ajustar os filtros ou remover algumas condições de busca.
            </p>
            {temFiltrosAtivos && (
              <button
                type="button"
                onClick={handleLimparFiltros}
                className={styles.clearFiltersButton}
              >
                Limpar todos os filtros
              </button>
            )}
          </div>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead className={styles.tableHeader}>
                <tr>
                  <th className={`${styles.tableHeaderCell} ${styles.sortableHeader}`} onClick={() => handleSort("nome")}>
                    <div className={styles.headerContent}>Nome do Projeto {getSortIcon("nome")}</div>
                  </th>
                  <th className={`${styles.tableHeaderCell} ${styles.sortableHeader}`} onClick={() => handleSort("dataInicio")}>
                    <div className={styles.headerContent}>Data Início {getSortIcon("dataInicio")}</div>
                  </th>
                  <th className={`${styles.tableHeaderCell} ${styles.sortableHeader}`} onClick={() => handleSort("dataFim")}>
                    <div className={styles.headerContent}>Data Fim {getSortIcon("dataFim")}</div>
                  </th>
                  <th className={`${styles.tableHeaderCell} ${styles.sortableHeader}`} onClick={() => handleSort("tutor")}>
                    <div className={styles.headerContent}>Tutor{getSortIcon("tutor")}</div>
                  </th>
                  <th className={`${styles.tableHeaderCell} ${styles.sortableHeader}`} onClick={() => handleSort("regiao")}>
                    <div className={styles.headerContent}>Região{getSortIcon("regiao")}</div>
                  </th>
                  <th className={`${styles.tableHeaderCell} ${styles.sortableHeader}`} onClick={() => handleSort("estado")}>
                    <div className={styles.headerContent}>Estado {getSortIcon("estado")}</div>
                  </th>
                  <th className={`${styles.tableHeaderCell} ${styles.sortableHeader}`} onClick={() => handleSort("cidade")}>
                    <div className={styles.headerContent}>Cidade {getSortIcon("cidade")}</div>
                  </th>
                  <th className={`${styles.tableHeaderCell} ${styles.sortableHeader}`} onClick={() => handleSort("formato")}>
                    <div className={styles.headerContent}>Formato {getSortIcon("formato")}</div>
                  </th>
                  <th className={`${styles.tableHeaderCell} ${styles.sortableHeader}`} onClick={() => handleSort("vagas")}>
                    <div className={styles.headerContent}>Vagas {getSortIcon("vagas")}</div>
                  </th>
                  <th className={styles.tableHeaderCell}>Ações</th>
                </tr>
              </thead>
              <tbody className={styles.tableBody}>
                {sortedProjetos.map((projeto) => (
                  <tr
                    key={projeto.id}
                    className={styles.tableRow}
                    onClick={() => handleRowClick(projeto)}
                    style={{ cursor: "pointer" }}
                  >
                    <td className={styles.tableCell}>
                      <div className={styles.projectTitle}>
                        <strong>{projeto.nome}</strong>
                        <span className={styles.projectInstitution}>
                          {projeto.instituicao}
                        </span>
                      </div>
                    </td>
                    <td className={styles.tableCell}>
                      {formatarData(projeto.dataInicio)}
                    </td>
                    <td className={styles.tableCell}>
                      {formatarData(projeto.dataFim)}
                    </td>
                    <td className={styles.tableCell}>
                      <div className={styles.tutorInfo} key={projeto.tutor?.id+''+projeto.tutor?.name}>
                        {/* <User size={14} className={styles.tutorIcon} /> */}
                        {/* {projeto.tutor.name} */}
                      </div>
                    </td>
                    <td className={styles.tableCell}>
                      <div className={styles.locationInfo} key={projeto.regiao?.id+''+projeto.regiao?.nome}>
                        {projeto.regiao?.nome}
                      </div>
                    </td>
                    <td className={styles.tableCell}>
                      <div className={styles.locationInfo} key={projeto.estado?.id+''+projeto.estado?.nome}>
                        {projeto.estado?.nome}
                      </div>
                    </td>
                    <td className={styles.tableCell}>
                      <div className={styles.locationInfo} key={projeto.cidade?.id+''+projeto.cidade?.nome}>
                        {projeto.cidade?.nome}
                      </div>
                    </td>
                    <td className={styles.tableCell}>
                      <span
                        className={`${styles.modalityBadge} ${
                          projeto.formato === "Remoto"
                            ? styles.modalityRemote
                            : styles.modalityPresencial
                        }`}
                      >
                        {projeto.formato.charAt(0).toUpperCase() + projeto.formato.slice(1)}
                      </span>
                    </td>
                    <td className={styles.tableCell}>
                      <span className={styles.vagasBadge}>{projeto.vagas}</span>
                    </td>
                    <td className={styles.tableCell}>
                      <button
                        type="button"
                        onClick={(e) => handleEditClick(e, projeto)}
                        className={styles.editButton}
                        title="Editar projeto"
                      >
                        <Edit size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <ModalDetalhesProjeto
        projeto={projetoSelecionado}
        isOpen={modalAberto}
        onClose={handleCloseModal}
        onEdit={handleEditProject}
      />
    </div>
  );
}
