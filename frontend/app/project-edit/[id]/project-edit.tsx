"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import SuccessModal from '@/components/sucess-modal/sucess-modal';
import styles from "../../project/projectform.module.css";
import { FormValidator, ValidationError } from "../../project/form-validation";
import UserAutocomplete from '@/components/user-autocomplete/user-autocomplete';
import { useRegioes } from '@/hooks/use-regioes';
import { useEstados } from '@/hooks/use-estados';
import { useCidades } from '@/hooks/use-cidades';
import { useEditProject } from '@/hooks/projects/use-edit-project';
import type { Project } from '@/types/project';

interface EditProjectProps {
  projectId: string;
}

export default function EditarProjeto({ projectId }: EditProjectProps) {
  const router = useRouter();

  const { project, isLoading, error: projectError, success: projectSuccess, atualizarProjeto } = useEditProject(projectId);
  const [projeto, setProjeto] = useState<Project | null>(null);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [isRemoto, setIsRemoto] = useState(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  
  // Formato de projeto
  const formatos = ["presencial", "remoto"];

  const isProjetoInicializado = useMemo(() => projeto !== null, [projeto]);

  const uf = useMemo(() => projeto?.estado?.uf || "", [projeto]);
  const regiaoEstado = useMemo(() => projeto?.regiao?.id || 0, [projeto]);
  const { cidades, isLoading: cidadesLoading } = useCidades(uf);
  const { regioes, isLoading: regioesLoading, error: regioesError } = useRegioes();
  const { filtrarEstadosPorRegiao, isLoading: estadosLoading } = useEstados();
  const [estados, setEstados] = useState([]);

  useEffect(() => {
    if (project && !isProjetoInicializado) {
      setProjeto(project);
      setIsRemoto(project.ehRemoto);
      setEstados(filtrarEstadosPorRegiao(project.regiao.id));
    }
  }, [project, isProjetoInicializado]);

  useEffect(() => {
    if (projectSuccess) {
      setIsSuccessModalOpen(true);
      const timer = setTimeout(() => router.push('/project-list'), 2000);
      return () => clearTimeout(timer);
    }
  }, [projectSuccess, router]);

  if (isLoading || !projeto) {
    return <div>Carregando projeto...</div>;
  }

  if (projectError) {
    return <div className={styles.errorMessage}>{projectError}</div>;
  }

  const handleInputChange = (field: keyof Project, value: any) => {
    console.log("Tutor selecionado", value)

    if(field === "estado") {
      setProjeto((prev) => ({ ...prev, [field]: value, cidade: null })); // limpa cidade ao mudar estado

    } else if(field === "regiao") {
      setProjeto((prev) => ({ ...prev, [field]: value, estado: null, cidade: null })); // limpa estado e cidade ao mudar região

      // Atualiza estados com base na região selecionada
      if(!isRemoto) {
        const estadosFiltrados = filtrarEstadosPorRegiao(value.id);
        setEstados(estadosFiltrados);
      }

    } else if(field === "formato") {
      setIsRemoto(value === "remoto");
      setProjeto((prev) => ({ ...prev, [field]: value }));
      setProjeto((prev) => ({ ...prev, ["ehRemoto"]: value === "remoto" }));

    }else {
      setProjeto((prev) => ({ ...prev, [field]: value }));
    }

    if (errors.length > 0) {
      setErrors((prev) => prev.filter((error) => error.field !== field))
    }
  };

  const handleUserChange = (tutor: any) => handleInputChange('tutor', tutor);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projeto) return;

    const validationErrors = FormValidator.validateProject(projeto);
    if (validationErrors.length) {
      setErrors(validationErrors);
      return;
    }

    await atualizarProjeto(projeto);
  };

  const getFieldError = (fieldName: string) => {
    var result = FormValidator.getFieldError(errors, fieldName);
    return result;
  };

  const hasFieldError = (fieldName: string) => {
    return !!getFieldError(fieldName);
  };

  return (
    <div className={styles.container}>
      <div className={styles.contentWrapper}> 
        <div className={`${styles.card} ${styles.spacer}`}>
          {/* Card Header */}
          <div className={styles.cardHeader}>
            <h2 className={styles.cardTitle}>Atualizar Projeto</h2>
          </div>

          {/* Card Content - Form*/}
          <div className={styles.cardContent}>
            {/* Error messages and Success Messages */}
            {getFieldError("general") && (
              <div className={styles.errorMessage}>{getFieldError("general")}</div>
            )}
            {successMessage && (
              <div className={styles.successMessage}>{successMessage}</div>
            )}


            {/* Project Form */}
            <form onSubmit={handleSubmit}>
              {/* Nome do Projeto: */}
              <div className={styles.formGroup}>
                <label htmlFor="nome" className={styles.label}>Nome do projeto <span className={styles.mandatory}>*</span></label>
                <input
                  id="nome"
                  value={projeto.nome}
                  onChange={(e) => handleInputChange("nome", e.target.value)}
                  className={`${styles.input} ${hasFieldError("nome") ? styles.inputError : ""}`}
                  placeholder="Digite o nome do projeto"
                />
                {hasFieldError("nome") && (
                  <span className={styles.fieldError}>
                    {getFieldError("nome")}
                  </span>
                )}
              </div>

              {/* Formato: (Presencial, Remoto, Híbrido) */}
              <div className={styles.formGroup}>
                <label htmlFor="formato" className={styles.label}> Formato <span className={styles.mandatory}>*</span></label>
                <select
                  id="formato"
                  value={projeto.formato}
                  onChange={(e) => { handleInputChange("formato", e.target.value) }}
                  className={`${styles.select} ${hasFieldError("formato") ? styles.inputError : "" }`}
                >
                  <option value="">Selecione o formato</option>
                  {formatos.map((formato) => (
                    <option key={formato} value={formato}> {formato.charAt(0).toUpperCase() + formato.slice(1)} </option>
                  ))}
                </select>
                {hasFieldError("formato") && (
                  <span className={styles.fieldError}> {getFieldError("formato")} </span>
                )}
              </div>


              {/* Regiões */}
              <div className={styles.formGroup}>
                <label htmlFor="regiao" className={styles.label}>Região <span className={styles.mandatory}>*</span></label>
                <select
                  id="regiao"
                  value={projeto.regiao?.id ?? 0}
                  onChange={(e) => {
                    const selectedId = Number(e.target.value);
                    const selectedRegiao = regioes.find(r => r.id === selectedId) || null;
                    handleInputChange("regiao", selectedRegiao)
                  }}
                  className={`${styles.select} ${hasFieldError("regiao") ? styles.inputError : "" }`}
                  disabled={regioesLoading}
                >
                  <option value={0}>Selecione a região</option>
                  {regioes.map((regiao) => (
                    <option key={regiao.id} value={regiao.id}>
                      {regiao.nome}
                    </option>
                  ))}
                </select>
                {hasFieldError("regiao") && (
                  <span className={styles.fieldError}>
                    {getFieldError("regiao")}
                  </span>
                )}
              </div>

              {!isRemoto && (
                <div>
                  {/* Estados e Cidades */}
                  <div className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}>
                    {/* Estados */}
                    <div className={styles.formGroup}>
                      <label htmlFor="estado" className={styles.label}>Estado <span className={styles.mandatory}>*</span></label>
                      <select
                        id="estado"
                        value={projeto.estado?.id || ""}
                        onChange={(e) => {
                          const selectedEstadoId = Number(e.target.value);
                          const selectedEstado = estados.find(estado => estado.id === selectedEstadoId) || null;
                          handleInputChange("estado", selectedEstado)
                        }}
                        className={`${styles.select} ${hasFieldError("estado") ? styles.inputError : "" }`}
                        disabled={estadosLoading || projeto.regiao === null}
                      >
                        <option value={0}>Selecione o estado</option>
                        {estados.map((estado) => (
                          <option key={estado.id} value={estado.id.toString()}>
                            {estado.nome}
                          </option>
                        ))}
                      </select>
                      {hasFieldError("estado") && (
                        <span className={styles.fieldError}>
                          {getFieldError("estado")}
                        </span>
                      )}

                    </div>

                    {/* Cidades */}
                    <div className={styles.formGroup}>
                      <label htmlFor="cidade" className={styles.label}>Cidade <span className={styles.mandatory}>*</span></label>
                      <select
                        id="cidade"
                        value={projeto.cidade?.id || ""}
                        onChange={(e) => {
                          const selectedCidadeId = Number(e.target.value);
                          const selectedCidade = cidades.find(cidade => cidade.id === selectedCidadeId) || null;
                          handleInputChange("cidade", selectedCidade)
                        }}
                        className={`${styles.select} ${hasFieldError("cidade") ? styles.inputError : "" }`}
                        disabled={cidadesLoading || projeto.estado === null}
                      >
                        <option value={0}>Selecione a cidade</option>
                        {cidades.map((cidade) => (
                          <option key={cidade.id} value={cidade.id.toString()}>
                            {cidade.nome}
                          </option>
                        ))}
                      </select>
                      {hasFieldError("cidade") && (
                        <span className={styles.fieldError}>
                          {getFieldError("cidade")}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Instituição */}
              <div className={styles.formGroup}>
                <label htmlFor="instituicao" className={styles.label}>Instituição de pesquisa <span className={styles.mandatory}>*</span></label>
                <input
                  id="instituicao"
                  value={projeto.instituicao}
                  onChange={(e) => handleInputChange("instituicao", e.target.value) }
                  className={`${styles.input} ${hasFieldError("instituicao") ? styles.inputError : "" }`}
                  placeholder="Nome da instituição"
                />
                {hasFieldError("instituicao") && (
                  <span className={styles.fieldError}>
                    {getFieldError("instituicao")}
                  </span>
                )} 
              </div>

              {/* Vagas */}
              <div className={styles.formGroup}>
                <label htmlFor="vagas" className={styles.label}>Número de vagas <span className={styles.mandatory}>*</span></label>
                <input
                  id="vagas"
                  type="number"
                  min="1"
                  value={projeto.vagas}
                  onChange={(e) => handleInputChange( "vagas", Number.parseInt(e.target.value) || 0)
                  }
                  className={`${styles.input} ${hasFieldError("vagas") ? styles.inputError : ""}`}
                  placeholder="10"
                />
                {hasFieldError("vagas") && (
                  <span className={styles.fieldError}>
                    {getFieldError("vagas")}
                  </span>
                )}
              </div>

              {/* Data de início e término do Projeto */}
              <div className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}>
                <div>
                  <label htmlFor="dataInicio" className={styles.label}> Data de início do projeto <span className={styles.mandatory}>*</span></label>
                  <input
                    id="dataInicio"
                    type="date"
                    value={projeto.dataInicio}
                    onChange={(e) => handleInputChange("dataInicio", e.target.value) }
                    className={`${styles.input} ${hasFieldError("dataInicio") ? styles.inputError : "" }`}
                  />
                  {hasFieldError("dataInicio") && (
                    <span className={styles.fieldError}>
                      {getFieldError("dataInicio")}
                    </span>
                  )}
                </div>
                <div>
                  <label htmlFor="dataFim" className={styles.label}>Data de término do projeto <span className={styles.mandatory}>*</span></label>
                  <input
                    id="dataFim"
                    type="date"
                    value={projeto.dataFim}
                    onChange={(e) => handleInputChange("dataFim", e.target.value) }
                    className={`${styles.input} ${hasFieldError("dataFim") ? styles.inputError : "" }`}
                  />
                  {hasFieldError("dataFim") && (
                    <span className={styles.fieldError}>
                      {getFieldError("dataFim")}
                    </span>
                  )}
                </div>
              </div>

              {/* Período de Inscrições */}
              <div className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}>
                <div>
                  <label htmlFor="inicioInscricoes" className={styles.label}>Início das inscrições <span className={styles.mandatory}>*</span></label>
                  <input
                    id="inicioInscricoes"
                    type="date"
                    value={projeto.inicioInscricoes}
                    onChange={(e) => handleInputChange("inicioInscricoes", e.target.value) }
                    className={`${styles.input} ${hasFieldError("inicioInscricoes") ? styles.inputError : "" }`}
                  />
                  {hasFieldError("inicioInscricoes") && (
                    <span className={styles.fieldError}>
                      {getFieldError("inicioInscricoes")}
                    </span>
                  )}
                </div>
                <div>
                  <label htmlFor="fimInscricoes" className={styles.label}>Fim das inscrições <span className={styles.mandatory}>*</span></label>
                  <input
                    id="fimInscricoes"
                    type="date"
                    value={projeto.fimInscricoes}
                    onChange={(e) => handleInputChange("fimInscricoes", e.target.value) }
                    className={`${styles.input} ${hasFieldError("fimInscricoes") ? styles.inputError : ""
                      }`}
                  />
                  {hasFieldError("fimInscricoes") && (
                    <span className={styles.fieldError}>
                      {getFieldError("fimInscricoes")}
                    </span>
                  )}
                </div>
              </div>

              {/* Tutor */}
              <div className={styles.formGroup}>
                {projeto.tutor.name}
                <label htmlFor="tutor" className={styles.label}>Tutor <span className={styles.mandatory}>*</span></label>
                <UserAutocomplete
                  groupName='tutor' 
                  value={project.tutor.id || ""} 
                  onChange={ handleUserChange } />
                  {hasFieldError("tutor") && <span className={styles.fieldError}>{getFieldError("tutor")}</span>}
              </div>

              {/* Resumo do Projeto */}
              <div className={styles.formGroup}>
                <label htmlFor="resumo" className={styles.label}>Resumo do projeto <span className={styles.mandatory}>*</span></label>
                <textarea
                  id="resumo"
                  value={projeto.descricao}
                  onChange={(e) => handleInputChange("descricao", e.target.value)}
                  className={`${styles.textarea} ${hasFieldError("descricao") ? styles.inputError : "" }`}
                  placeholder="Digite o resumo do projeto"
                />
                {hasFieldError("descricao") && (
                  <span className={styles.fieldError}>
                    {getFieldError("descricao")}
                  </span>
                )}
              </div>


              {/* Botao Salvar */}
              <button
                type="submit"
                className={styles.button}
                disabled={
                  isLoading ||
                  regioesLoading ||
                  estadosLoading
                }
              >
                {isLoading ? "Salvando..." : "Atualizar projeto"}
              </button>

            </form>

          </div>
        </div>
      </div>

      <SuccessModal 
        isOpen={isSuccessModalOpen} 
        message={projectSuccess}
        onClose={() => {
          setIsSuccessModalOpen(false)
          router.push("/project-list");
        }} 
      />
    </div>
  );
}
