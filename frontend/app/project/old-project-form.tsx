"use client";

import type React from "react";
import { useState, useEffect } from "react";
import styles from "./projectform.module.css";
import { ProjectService } from "@/services/projectService";
import { FormValidator, type ValidationError } from "./form-validation";
import type { ProjectFormData } from "@/types/project";
import { useProjects } from "@/hooks/projects/use-projects";
import { useTutores } from "@/hooks/use-users";
import { useRegioes } from "@/hooks/use-regioes";
import { useEstadosDinamicos } from "@/hooks/use-estados-dinamicos";
import { useCidades } from "@/hooks/use-cidades";

const projetoDefault: ProjectFormData = {
  titulo: "",
  estado: null,
  cidade: null,
  formato: "",
  instituicao: "",
  resumo: "",
  vagas: 10,
  dataInicio: "",
  dataFim: "",
  inicioInscricoes: "",
  fimInscricoes: "",
  regioesAceitas: [],
  tutor: null,
};

export default function ProjectForm() {
  const [projeto, setProjeto] = useState<ProjectFormData>(projetoDefault);
  // const [projetos, setProjetos] = useState<ProjectFormData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [successMessage, setSuccessMessage] = useState("");
  
  const formatos = ["Presencial", "Remoto"];
  const [estadoSelecionado, setEstadoSelecionado] = useState("");
  const { criarProjeto } = useProjects();

  // Hooks para carregar dados
  const { regioes, isLoading: regioesLoading, error: regioesError } = useRegioes();
  const { tutores, isLoading: tutoresLoading, error: tutoresError, recarregarTutores } = useTutores();

  // Estados dinâmicos baseados nas regiões selecionadas
  const regioesIds = projeto.regioesAceitas.map((regiao) => regiao.id);
  const { estados, isLoading: estadosLoading, error: estadosError } = useEstadosDinamicos(regioesIds);
  // Cidades baseadas no estado selecionado
  const { cidades, isLoading: cidadesLoading, error: cidadesError } = useCidades(estadoSelecionado);


  // Limpar cidade quando estado mudar
  // useEffect(() => {
  //   if (projeto.estado !== "" && projeto.cidade !== "") {
  //     setProjeto((prev) => ({ ...prev, cidade: "" }));
  //   }
  // }, [projeto.estado]);

  // // Limpar estado e cidade quando região mudar
  // useEffect(() => {
  //   setProjeto((prev) => ({ ...prev, estado: "", cidade: "" }));
  //   setEstadoSelecionado("");
  // }, [projeto.regioesAceitas]);

  // // Adicionar useEffect para limpar campos quando formato mudar para remoto
  // useEffect(() => {
  //   if (projeto.formato.toLowerCase() === "remoto") {
  //     setProjeto((prev) => ({
  //       ...prev,
  //       regioesAceitas: [],
  //       estado: "",
  //       cidade: "",
  //     }));
  //     setEstadoSelecionado("");
  //   }
  // }, [projeto.formato]);

  const handleInputChange = (
    field: keyof ProjectFormData,
    value: string | number | string[]
  ) => {
    setProjeto((prev) => ({
      ...prev,
      [field]: value,
    }));

    if (errors.length > 0) {
      setErrors((prev) => prev.filter((error) => error.field !== field));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMessage("");

    // // Todas regiões, quando for remoto
    // if (projeto.formato.toLowerCase() === "remoto") {
    //   projeto.regioesAceitas = ["N", "S", "NE", "SE", "CO"];
    // }

    // Validate form data
    const validationErrors = FormValidator.validateProject(projeto);

    console.log("validation errors", validationErrors);

    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsLoading(true);
    setErrors([]);

    e.preventDefault();
    await criarProjeto(projeto);
    

    // try {
    //   const response = await ProjectService.criarProject(projeto);

    //   if (response.success) {
    //     setProjetos((prev) => [...prev, projeto]);
    //     setProjeto(projetoDefault);
    //     setEstadoSelecionado("");
    //     setSuccessMessage("Projeto cadastrado com sucesso!");
    //   } else {
    //     setErrors([{ field: "general", message: response.message }]);
    //   }
    // } catch (error) {
    //   console.error("Erro ao cadastrar projeto:", error);
    //   setErrors([
    //     { field: "general", message: "Erro inesperado ao cadastrar projeto" },
    //   ]);
    // } finally {
    //   setIsLoading(false);
    // }
  };

  const getFieldError = (fieldName: string) => {
    return FormValidator.getFieldError(errors, fieldName);
  };

  const hasFieldError = (fieldName: string) => {
    return !!getFieldError(fieldName);
  };

  // Adicionar variável para verificar se é remoto
  const isRemoto = projeto.formato.toLowerCase() === "remoto";

  return (
    <div className={styles.container}>
      <div className={styles.contentWrapper}>
        <div className={`${styles.card} ${styles.spacer}`}>
          <div className={styles.cardHeader}>
            <h2 className={styles.cardTitle}>Cadastro de projetos</h2>
          </div>
          <div className={styles.cardContent}>
            {getFieldError("general") && (
              <div className={styles.errorMessage}>
                {getFieldError("general")}
              </div>
            )}

            {regioesError && (
              <div className={styles.errorMessage}>
                Erro ao carregar regiões: {regioesError}
              </div>
            )}

            {successMessage && (
              <div className={styles.successMessage}>{successMessage}</div>
            )}

            <form onSubmit={handleSubmit}>
              <div className={styles.formGroup}>
                <label htmlFor="titulo" className={styles.label}>
                  Título do projeto *
                </label>
                <input
                  id="titulo"
                  value={projeto.titulo}
                  onChange={(e) => handleInputChange("titulo", e.target.value)}
                  className={`${styles.input} ${hasFieldError("titulo") ? styles.inputError : ""
                    }`}
                  placeholder="Digite o título do projeto"
                />
                {hasFieldError("titulo") && (
                  <span className={styles.fieldError}>
                    {getFieldError("titulo")}
                  </span>
                )}
              </div>

              {/* Formato */}
              <div className={styles.formGroup}>
                <label htmlFor="formato" className={styles.label}>
                  Formato *
                </label>
                <select
                  id="formato"
                  value={projeto.formato}
                  onChange={(e) => handleInputChange("formato", e.target.value)}
                  className={`${styles.select} ${hasFieldError("formato") ? styles.inputError : ""
                    }`}
                >
                  <option value="">Selecione o formato</option>
                  {formatos.map((formato) => (
                    <option key={formato} value={formato}>
                      {formato}
                    </option>
                  ))}
                </select>
                {hasFieldError("formato") && (
                  <span className={styles.fieldError}>
                    {getFieldError("formato")}
                  </span>
                )}
              </div>

              {/* Regiões */}
              {!isRemoto && (
                <div className={styles.formGroup}>
                  <label htmlFor="regiao" className={styles.label}>
                    Região aceita *
                  </label>
                  {regioesLoading ? (
                    <div className={styles.loadingText}>
                      Carregando regiões...
                    </div>
                  ) : (
                    <select
                      id="regiao"
                      value={projeto.regioesAceitas[0] || ""}
                      onChange={(e) =>
                        handleInputChange(
                          "regioesAceitas",
                          e.target.value ? [e.target.value] : []
                        )
                      }
                      className={`${styles.select} ${hasFieldError("regioesAceitas") ? styles.inputError : ""
                        }`}
                    >
                      <option value="">Selecione uma região</option>
                      {regioes.map((regiao) => (
                        <option key={regiao.id} value={regiao.id.toString()}>
                          {regiao.nome} ({regiao.abreviacao})
                        </option>
                      ))}
                    </select>
                  )}
                  {hasFieldError("regioesAceitas") && (
                    <span className={styles.fieldError}>
                      {getFieldError("regioesAceitas")}
                    </span>
                  )}
                </div>
              )}

              {/* Estado, Cidade */}
              {!isRemoto && (
                <div
                  className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}
                >
                  <div>
                    <label htmlFor="estado" className={styles.label}>
                      Estado *
                    </label>
                    <select
                      id="estado"
                      value={projeto.estado}
                      onChange={(e) =>
                        handleInputChange("estado", e.target.value)
                      }
                      className={`${styles.select} ${hasFieldError("estado") ? styles.inputError : ""
                        }`}
                      disabled={
                        estadosLoading || projeto.regioesAceitas.length === 0
                      }
                    >
                      <option value="">
                        {projeto.regioesAceitas.length === 0
                          ? "Selecione uma região primeiro"
                          : estadosLoading
                            ? "Carregando estados..."
                            : "Selecione o estado"}
                      </option>
                      {estados.map((estado) => (
                        <option key={estado.id} value={estado.id}>
                          {estado.nome} ({estado.uf})
                        </option>
                      ))}
                    </select>
                    {hasFieldError("estado") && (
                      <span className={styles.fieldError}>
                        {getFieldError("estado")}
                      </span>
                    )}
                    {estadosError && (
                      <span className={styles.fieldError}>{estadosError}</span>
                    )}
                  </div>

                  <div>
                    <label htmlFor="cidade" className={styles.label}>
                      Cidade *
                    </label>
                    <select
                      id="cidade"
                      value={projeto.cidade}
                      onChange={(e) =>
                        handleInputChange("cidade", e.target.value)
                      }
                      className={`${styles.select} ${hasFieldError("cidade") ? styles.inputError : ""
                        }`}
                      disabled={cidadesLoading || !projeto.estado}
                    >
                      <option value="">
                        {!projeto.estado
                          ? "Selecione um estado primeiro"
                          : cidadesLoading
                            ? "Carregando cidades..."
                            : "Selecione a cidade"}
                      </option>
                      {cidades.map((cidade) => (
                        <option key={cidade.id} value={cidade.id}>
                          {cidade.nome}
                        </option>
                      ))}
                    </select>
                    {hasFieldError("cidade") && (
                      <span className={styles.fieldError}>
                        {getFieldError("cidade")}
                      </span>
                    )}
                    {cidadesError && (
                      <span className={styles.fieldError}>{cidadesError}</span>
                    )}
                  </div>
                </div>
              )}

              <div
                className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}
              >
                <div>
                  <label htmlFor="instituicao" className={styles.label}>
                    Instituição de pesquisa *
                  </label>
                  <input
                    id="instituicao"
                    value={projeto.instituicao}
                    onChange={(e) =>
                      handleInputChange("instituicao", e.target.value)
                    }
                    className={`${styles.input} ${hasFieldError("instituicao") ? styles.inputError : ""
                      }`}
                    placeholder="Digite a instituição de pesquisa"
                  />
                  {hasFieldError("instituicao") && (
                    <span className={styles.fieldError}>
                      {getFieldError("instituicao")}
                    </span>
                  )}
                </div>
                <div>
                  <label htmlFor="vagas" className={styles.label}>
                    Número de vagas *
                  </label>
                  <input
                    id="vagas"
                    type="number"
                    min="1"
                    value={projeto.vagas}
                    onChange={(e) =>
                      handleInputChange(
                        "vagas",
                        Number.parseInt(e.target.value) || 0
                      )
                    }
                    className={`${styles.input} ${hasFieldError("vagas") ? styles.inputError : ""
                      }`}
                    placeholder="20"
                  />
                  {hasFieldError("vagas") && (
                    <span className={styles.fieldError}>
                      {getFieldError("vagas")}
                    </span>
                  )}
                </div>
              </div>

              <div
                className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}
              >
                <div>
                  <label htmlFor="dataInicio" className={styles.label}>
                    Data de início *
                  </label>
                  <input
                    id="dataInicio"
                    type="date"
                    value={projeto.dataInicio}
                    onChange={(e) =>
                      handleInputChange("dataInicio", e.target.value)
                    }
                    className={`${styles.input} ${hasFieldError("dataInicio") ? styles.inputError : ""
                      }`}
                  />
                  {hasFieldError("dataInicio") && (
                    <span className={styles.fieldError}>
                      {getFieldError("dataInicio")}
                    </span>
                  )}
                </div>
                <div>
                  <label htmlFor="dataFim" className={styles.label}>
                    Data de fim *
                  </label>
                  <input
                    id="dataFim"
                    type="date"
                    value={projeto.dataFim}
                    onChange={(e) =>
                      handleInputChange("dataFim", e.target.value)
                    }
                    className={`${styles.input} ${hasFieldError("dataFim") ? styles.inputError : ""
                      }`}
                  />
                  {hasFieldError("dataFim") && (
                    <span className={styles.fieldError}>
                      {getFieldError("dataFim")}
                    </span>
                  )}
                </div>
              </div>

              <div
                className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}
              >
                <div>
                  <label htmlFor="inicioInscricoes" className={styles.label}>
                    Início das inscrições *
                  </label>
                  <input
                    id="inicioInscricoes"
                    type="date"
                    value={projeto.inicioInscricoes}
                    onChange={(e) =>
                      handleInputChange("inicioInscricoes", e.target.value)
                    }
                    className={`${styles.input} ${hasFieldError("inicioInscricoes") ? styles.inputError : ""
                      }`}
                  />
                  {hasFieldError("inicioInscricoes") && (
                    <span className={styles.fieldError}>
                      {getFieldError("inicioInscricoes")}
                    </span>
                  )}
                </div>
                <div>
                  <label htmlFor="fimInscricoes" className={styles.label}>
                    Fim das inscrições *
                  </label>
                  <input
                    id="fimInscricoes"
                    type="date"
                    value={projeto.fimInscricoes}
                    onChange={(e) =>
                      handleInputChange("fimInscricoes", e.target.value)
                    }
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

              <div className={styles.formGroup}>
                <label htmlFor="tutorId" className={styles.label}>
                  Tutor *
                </label>
                {tutoresError && (
                  <div
                    className={styles.errorMessage}
                    style={{ marginBottom: "0.5rem", fontSize: "0.75rem" }}
                  >
                    {tutoresError}
                    <button
                      type="button"
                      onClick={recarregarTutores}
                      className={styles.retryButton}
                      style={{ marginLeft: "0.5rem" }}
                    >
                      Tentar novamente
                    </button>
                  </div>
                )}
                <select
                  id="tutorId"
                  value={projeto.tutorId}
                  onChange={(e) => handleInputChange("tutorId", e.target.value)}
                  className={`${styles.select} ${hasFieldError("tutorId") ? styles.inputError : ""
                    }`}
                  disabled={tutoresLoading}
                >
                  <option value="">
                    {tutoresLoading
                      ? "Carregando tutores..."
                      : "Selecione um tutor"}
                  </option>
                  {tutores.map((tutor) => (
                    <option key={tutor.id} value={tutor.id}>
                      {tutor.nome} - {tutor.email}
                    </option>
                  ))}
                </select>
                {hasFieldError("tutorId") && (
                  <span className={styles.fieldError}>
                    {getFieldError("tutorId")}
                  </span>
                )}
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="resumo" className={styles.label}>
                  Descrição do projeto *
                </label>
                <textarea
                  id="resumo"
                  value={projeto.resumo}
                  onChange={(e) => handleInputChange("resumo", e.target.value)}
                  className={`${styles.textarea} ${hasFieldError("resumo") ? styles.inputError : ""
                    }`}
                  placeholder="Digite a descrição detalhada do projeto"
                />
                {hasFieldError("resumo") && (
                  <span className={styles.fieldError}>
                    {getFieldError("resumo")}
                  </span>
                )}
              </div>

              <button
                type="submit"
                className={styles.button}
                disabled={
                  isLoading ||
                  regioesLoading ||
                  estadosLoading ||
                  tutoresLoading
                }
              >
                {isLoading ? "Salvando..." : "Salvar projeto"}
              </button>
            </form>
          </div>
        </div>

        {/* {projetos.length > 0 && (
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <h2 className={styles.cardTitle}>Resumo dos Projetos</h2>
            </div>
            <div className={styles.cardContent}>
              <div className={styles.projectList}>
                {projetos.map((proj, index) => (
                  <div key={index} className={styles.projectItem}>
                    <h3 className={styles.projectTitle}>{proj.titulo}</h3>
                    <p className={styles.projectMeta}>
                      {proj.instituicao}
                      {proj.formato.toLowerCase() !== "remoto" &&
                        ` - ${getCidadeNome(proj.cidade)}, ${getEstadoNome(
                          proj.estado
                        )}`}
                    </p>
                    <p className={styles.projectMeta}>
                      Formato: {proj.formato} | Vagas: {proj.vagas}
                    </p>
                    {proj.formato.toLowerCase() !== "remoto" && (
                      <p className={styles.projectMeta}>
                        Região: {getRegiaoNomes(proj.regioesAceitas)}
                      </p>
                    )}
                    <p className={styles.projectMeta}>
                      Tutor: {getTutorNome(proj.tutorId)}
                    </p>
                    <p className={styles.projectDescription}>{proj.resumo}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )} */}
      </div>
    </div>
  );
}
