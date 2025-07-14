import React from "react";
import {
  Filter,
  X,
  Search,
  Calendar,
  User,
  MapPin,
  Building,
} from "lucide-react";
import styles from "../projectlist.module.css";
import type { FiltrosProjects } from "@/types/project";
import { Estado } from "@/types/estado";
import { User as UserType } from "@/types/user";
import { Regiao } from "@/types/regiao";

interface FilterGroupProps {
  filtros: FiltrosProjects;
  onFiltroChange: (campo: keyof FiltrosProjects, valor: string) => void;
  onAplicar: () => void;
  onLimpar: () => void;
  onFechar: () => void;
  onToggle: () => void;
  mostrar: boolean;
  regioes: Regiao[]
  estados: Estado[];
  formatos: string[];
  tutores: UserType[];
  temFiltrosAtivos: boolean;
  isLoading: boolean;
  totalProjetos: number;
  qtdeProjetosFiltrados: number;
}

export default function FilterGroup({
  filtros,
  onFiltroChange,
  onAplicar,
  onLimpar,
  onFechar,
  onToggle,
  mostrar,
  regioes,
  estados,
  formatos,
  tutores,
  temFiltrosAtivos,
  isLoading,
  totalProjetos,
  qtdeProjetosFiltrados
}: FilterGroupProps) {
  return (
    <>
      {/* Header da página */}
      <div className={styles.pageHeader}>
        <div>
          <h1 className={styles.pageTitle}>Lista de Projetos</h1>
          <p className={styles.pageSubtitle}>
            {isLoading
              ? "Carregando projetos..."
              : `${qtdeProjetosFiltrados} de ${totalProjetos} projetos encontrados`}
          </p>
        </div>
        <button
          type="button"
          onClick={onToggle}
          className={`${styles.filterButton} ${
            mostrar ? styles.filterButtonActive : ""
          }`}
        >
          <Filter size={16} /> Filtros{" "}
          {temFiltrosAtivos && <span className={styles.filterBadge}></span>}
        </button>
      </div>

      {mostrar && (
        <div className={styles.filterPanel}>
          <div className={styles.filterHeader}>
            <h3 className={styles.filterTitle}>
              <Filter size={16} /> Filtrar Projetos
            </h3>
            <button
              type="button"
              onClick={onFechar}
              className={styles.closeButton}
              aria-label="Fechar filtros"
            >
              <X size={16} />
            </button>
          </div>

          <div className={styles.filterContent}>
            <div className={styles.filterGrid}>
              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <Search size={14} /> Título do Projeto
                </label>
                <input
                  type="text"
                  value={filtros.titulo || ""}
                  onChange={(e) => onFiltroChange("titulo", e.target.value)}
                  className={styles.filterInput}
                  placeholder="Buscar por título..."
                />
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <User size={14} /> Tutor
                </label>
                <select
                  value={filtros.tutorId || ""}
                  onChange={(e) => onFiltroChange("tutorId", e.target.value)}
                  className={styles.filterSelect}
                >
                  <option value="">Todos os tutores</option>
                  {tutores.map((tutor) => (
                    <option key={tutor.id} value={tutor.id}>
                      {tutor.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <MapPin size={14} /> Região
                </label>
                <select
                  value={filtros.regiao || ""}
                  onChange={(e) => onFiltroChange("regiao", e.target.value)}
                  className={styles.filterSelect}
                >
                  <option value="">Todas as regiões</option>
                  {regioes.map((regiao) => (
                    <option key={regiao.id} value={regiao.id}>
                      {regiao.nome}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <MapPin size={14} /> Estado
                </label>
                <select
                  value={filtros.estado || ""}
                  onChange={(e) => onFiltroChange("estado", e.target.value)}
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

              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <MapPin size={14} /> Cidade
                </label>
                <input
                  type="text"
                  value={filtros.cidade || ""}
                  onChange={(e) => onFiltroChange("cidade", e.target.value)}
                  className={styles.filterInput}
                  placeholder="Buscar por cidade..."
                />
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>Formato</label>
                <select
                  value={filtros.formato || ""}
                  onChange={(e) => onFiltroChange("formato", e.target.value)}
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

              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <Building size={14} /> Instituição
                </label>
                <input
                  type="text"
                  value={filtros.instituicao || ""}
                  onChange={(e) =>
                    onFiltroChange("instituicao", e.target.value)
                  }
                  className={styles.filterInput}
                  placeholder="Buscar por instituição..."
                />
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <Calendar size={14} /> Data Início (a partir de)
                </label>
                <input
                  type="date"
                  value={filtros.dataInicio || ""}
                  onChange={(e) => onFiltroChange("dataInicio", e.target.value)}
                  className={styles.filterInput}
                />
              </div>

              <div className={styles.filterGroup}>
                <label className={styles.filterLabel}>
                  <Calendar size={14} /> Data Fim (até)
                </label>
                <input
                  type="date"
                  value={filtros.dataFim || ""}
                  onChange={(e) => onFiltroChange("dataFim", e.target.value)}
                  className={styles.filterInput}
                />
              </div>
            </div>

            <div className={styles.filterActions}>
              <button
                type="button"
                onClick={onLimpar}
                className={styles.clearButton}
              >
                Limpar Filtros
              </button>
              <button
                type="button"
                onClick={onAplicar}
                className={styles.applyButton}
              >
                Aplicar Filtros
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
