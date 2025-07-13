"use client"

import type React from "react"

import { X, Calendar, User, MapPin, Building, Users, FileText } from "lucide-react"
import styles from "./modalprojectdetail.module.css"
import type { Project } from "@/types/project"

interface ModalDetalhesProjetoProps {
  projeto: Project | null
  isOpen: boolean
  onClose: () => void
  onEdit: (projeto: Project) => void
}

export default function ModalDetalhesProjeto({
  projeto,
  isOpen,
  onClose,
  onEdit,
}: ModalDetalhesProjetoProps) {
  if (!isOpen || !projeto) return null

  const formatarData = (data: string) => {
    return new Date(data).toLocaleDateString("pt-BR")
  }

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onEdit(projeto)
  }

  return (
    <div className={styles.overlay} onClick={handleOverlayClick}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h2 className={styles.title}>Detalhes do Projeto</h2>
          <button type="button" onClick={onClose} className={styles.closeButton} aria-label="Fechar modal">
            <X size={20} />
          </button>
        </div>

        <div className={styles.content}>
          <div className={styles.section}>
            <h3 className={styles.projectTitle}>{projeto.nome}</h3>
            <div className={styles.institutionBadge}>
              <Building size={16} />
              {projeto.instituicao}
            </div>
          </div>

          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <div className={styles.infoLabel}>
                <Calendar size={16} />
                Data de Início
              </div>
              <div className={styles.infoValue}>{formatarData(projeto.dataInicio)}</div>
            </div>

            <div className={styles.infoItem}>
              <div className={styles.infoLabel}>
                <Calendar size={16} />
                Data de Fim
              </div>
              <div className={styles.infoValue}>{formatarData(projeto.dataFim)}</div>
            </div>

            <div className={styles.infoItem}>
              <div className={styles.infoLabel}>
                <User size={16} />
                Tutor
              </div>
              <div className={styles.infoValue}>{projeto.tutor.name}</div>
            </div>

            <div className={styles.infoItem}>
              <div className={styles.infoLabel}>
                <Users size={16} />
                Vagas
              </div>
              <div className={styles.infoValue}>{projeto.vagas}</div>
            </div>

            <div className={styles.infoItem}>
              <div className={styles.infoLabel}>
                <MapPin size={16} />
                Localização
              </div>
              <div className={styles.infoValue}>
                {projeto.cidade.nome}, {projeto.estado.nome}
              </div>
            </div>

            <div className={styles.infoItem}>
              <div className={styles.infoLabel}>Modalidade</div>
              <div className={styles.infoValue}>
                <span
                  className={`${styles.modalityBadge} ${
                    projeto.formato === "Remoto" ? styles.modalityRemote : styles.modalityPresencial
                  }`}
                >
                  {projeto.formato}
                </span>
              </div>
            </div>
          </div>

          
          <div className={styles.section}>
            <div className={styles.infoLabel}>Região</div>
            <div className={styles.regionsList}>
              <span key={projeto.regiao.id} className={styles.regionBadge}>
                {projeto.regiao.nome}
              </span>
            </div>
          </div>
          

          <div className={styles.section}>
            <div className={styles.infoLabel}>
              <FileText size={16} />
              Resumo do Projeto
            </div>
            <div className={styles.description}>{projeto.descricao}</div>
          </div>
        </div>

        <div className={styles.footer}>
          <button type="button" onClick={onClose} className={styles.cancelButton}>
            Fechar
          </button>
          <button type="button" onClick={handleEditClick} className={styles.editButton}>
            Editar Projeto
          </button>
        </div>
      </div>
    </div>
  )
}
