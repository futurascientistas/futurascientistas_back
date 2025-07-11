// "use client"

// import type React from "react"
// import { useState, useEffect } from "react"
// import { ArrowLeft } from "lucide-react"
// import styles from "../project/projectform.module.css"
// import { FormValidator, type ValidationError } from "../project/form-validation"
// import type { ProjectFormData, ProjectListItem } from "@/types/project"
// import { useTutores } from "@/hooks/use-users"
// import { useRegioes } from "@/hooks/use-regioes"
// import { useEstadosDinamicos } from "@/hooks/use-estados-dinamicos"
// import { useCidades } from "@/hooks/use-cidades"

// interface EdicaoProjetoProps {
//   projeto: ProjectListItem
//   onVoltar: () => void
//   onSalvar: (projeto: ProjectFormData) => void
// }

// export default function EdicaoProjeto({ projeto, onVoltar, onSalvar }: EdicaoProjetoProps) {
//   const [projetoEditado, setProjetoEditado] = useState<ProjectFormData>({
//     titulo: "",
//     estado: "",
//     cidade: "",
//     formato: "",
//     instituicao: "",
//     resumo: "",
//     vagas: 20,
//     dataInicio: "",
//     dataFim: "",
//     inicioInscricoes: "",
//     fimInscricoes: "",
//     regioesAceitas: [],
//     tutorId: "",
//   })

//   const [isLoading, setIsLoading] = useState(false)
//   const [errors, setErrors] = useState<ValidationError[]>([])
//   const [successMessage, setSuccessMessage] = useState("")
//   const [estadoSelecionado, setEstadoSelecionado] = useState("")

//   const [isDeactivating, setIsDeactivating] = useState(false)
//   const [showDeactivateConfirm, setShowDeactivateConfirm] = useState(false)

//   // Hooks para carregar dados
//   const { regioes, isLoading: regioesLoading, error: regioesError } = useRegioes()
//   const { tutores, isLoading: tutoresLoading, error: tutoresError, recarregarTutores } = useTutores()

//   // Estados dinâmicos baseados nas regiões selecionadas
//   const regioesIds = projetoEditado.regioesAceitas.map((id) => Number.parseInt(id))
//   const { estados, isLoading: estadosLoading, error: estadosError } = useEstadosDinamicos(regioesIds)

//   // Cidades baseadas no estado selecionado
//   const { cidades, isLoading: cidadesLoading, error: cidadesError } = useCidades(estadoSelecionado)

//   const formatos = ["Presencial", "Remoto"]

//   // Carregar dados do projeto quando o componente montar
//   useEffect(() => {
//     if (projeto) {
//       setProjetoEditado({
//         titulo: projeto.titulo,
//         estado: projeto.estado,
//         cidade: projeto.cidade,
//         formato: projeto.formato,
//         instituicao: projeto.instituicao,
//         resumo: projeto.resumo,
//         vagas: projeto.vagas,
//         dataInicio: projeto.dataInicio,
//         dataFim: projeto.dataFim,
//         inicioInscricoes: projeto.inicioInscricoes || "",
//         fimInscricoes: projeto.fimInscricoes || "",
//         regioesAceitas: projeto.regioesAceitas || [],
//         tutorId: projeto.tutorId,
//       })

//       // Definir estado selecionado para carregar cidades
//       if (projeto.estado && estados.length > 0) {
//         const estado = estados.find((e) => e.id.toString() === projeto.estado)
//         if (estado) {
//           setEstadoSelecionado(estado.uf)
//         }
//       }
//     }
//   }, [projeto, estados])

//   // Atualizar UF do estado selecionado quando o estado mudar
//   useEffect(() => {
//     if (projetoEditado.estado) {
//       const estado = estados.find((e) => e.id.toString() === projetoEditado.estado)
//       if (estado) {
//         setEstadoSelecionado(estado.uf)
//       }
//     } else {
//       setEstadoSelecionado("")
//     }
//   }, [projetoEditado.estado, estados])

//   // Limpar cidade quando estado mudar
//   useEffect(() => {
//     if (projetoEditado.estado !== projeto.estado && projetoEditado.cidade !== "") {
//       setProjetoEditado((prev) => ({ ...prev, cidade: "" }))
//     }
//   }, [projetoEditado.estado, projeto.estado])

//   // Limpar estado e cidade quando região mudar
//   useEffect(() => {
//     const regioesOriginais = projeto.regioesAceitas || []
//     const regioesAtuais = projetoEditado.regioesAceitas

//     // Verificar se as regiões mudaram
//     const regioesChanged =
//       regioesOriginais.length !== regioesAtuais.length || regioesOriginais.some((r) => !regioesAtuais.includes(r))

//     if (regioesChanged && regioesAtuais.length > 0) {
//       setProjetoEditado((prev) => ({ ...prev, estado: "", cidade: "" }))
//       setEstadoSelecionado("")
//     }
//   }, [projetoEditado.regioesAceitas, projeto.regioesAceitas])

//   // Limpar campos quando modalidade mudar para remoto
//   // useEffect(() => {
//   //   if (projetoEditado.formato.toLowerCase() === "remoto" && projeto.formato.toLowerCase() !== "remoto") {
//   //     setProjetoEditado((prev) => ({
//   //       ...prev,
//   //       regioesAceitas: [],
//   //       estado: "",
//   //       cidade: "",
//   //     }))
//   //     setEstadoSelecionado("")
//   //   }
//   // }, [projetoEditado.formato, projeto.formato])

//   const handleInputChange = (field: keyof ProjectFormData, value: string | number | string[]) => {
//     setProjetoEditado((prev) => ({
//       ...prev,
//       [field]: value,
//     }))

//     if (errors.length > 0) {
//       setErrors((prev) => prev.filter((error) => error.field !== field))
//     }
//   }

//   const handleDeactivate = async () => {
//     setIsDeactivating(true)
//     setErrors([])

//     try {
//       // Simular desativação do projeto
//       await new Promise((resolve) => setTimeout(resolve, 1000))

//       setSuccessMessage("Projeto desativado com sucesso!")

//       // Voltar para a lista após 2 segundos
//       setTimeout(() => {
//         onVoltar()
//       }, 2000)
//     } catch (error) {
//       console.error("Erro ao desativar projeto:", error)
//       setErrors([{ field: "general", message: "Erro inesperado ao desativar projeto" }])
//     } finally {
//       setIsDeactivating(false)
//       setShowDeactivateConfirm(false)
//     }
//   }

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault()
//     setSuccessMessage("")

//     const validationErrors = FormValidator.validateProject(projetoEditado)
//     if (validationErrors.length > 0) {
//       setErrors(validationErrors)
//       return
//     }

//     setIsLoading(true)
//     setErrors([])

//     try {
//       // Simular atualização do projeto
//       await new Promise((resolve) => setTimeout(resolve, 1000))

//       setSuccessMessage("Projeto atualizado com sucesso!")
//       onSalvar(projetoEditado)

//       // Voltar para a lista após 2 segundos
//       setTimeout(() => {
//         onVoltar()
//       }, 2000)
//     } catch (error) {
//       console.error("Erro ao atualizar projeto:", error)
//       setErrors([{ field: "general", message: "Erro inesperado ao atualizar projeto" }])
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   const getFieldError = (fieldName: string) => {
//     return FormValidator.getFieldError(errors, fieldName)
//   }

//   const hasFieldError = (fieldName: string) => {
//     return !!getFieldError(fieldName)
//   }

//   const isRemoto = true //projetoEditado.formato.toLowerCase() === "remoto"

//   // Fechar modal com ESC
//   useEffect(() => {
//     const handleKeyDown = (event: KeyboardEvent) => {
//       if (event.key === "Escape" && showDeactivateConfirm) {
//         setShowDeactivateConfirm(false)
//       }
//     }

//     if (showDeactivateConfirm) {
//       document.addEventListener("keydown", handleKeyDown)
//       return () => document.removeEventListener("keydown", handleKeyDown)
//     }
//   }, [showDeactivateConfirm])

//   return (
//     <div className={styles.container}>
//       <div className={styles.contentWrapper}>
//         <div className={styles.welcomeCard}>
//           <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1rem" }}>
//             <button
//               type="button"
//               onClick={onVoltar}
//               style={{
//                 display: "flex",
//                 alignItems: "center",
//                 gap: "0.5rem",
//                 padding: "0.5rem 1rem",
//                 background: "#f3f4f6",
//                 border: "1px solid #d1d5db",
//                 borderRadius: "0.375rem",
//                 color: "#374151",
//                 cursor: "pointer",
//                 fontSize: "0.875rem",
//                 fontWeight: "500",
//                 transition: "all 0.2s",
//               }}
//               onMouseOver={(e) => {
//                 e.currentTarget.style.background = "#e5e7eb"
//               }}
//               onMouseOut={(e) => {
//                 e.currentTarget.style.background = "#f3f4f6"
//               }}
//             >
//               <ArrowLeft size={16} />
//               Voltar para Lista
//             </button>
//           </div>
//           <h1 className={styles.welcomeTitle}>Editar Projeto</h1>
//           <p className={styles.welcomeText}>Modifique as informações do projeto conforme necessário.</p>
//         </div>

//         <div className={`${styles.card} ${styles.spacer}`}>
//           <div className={styles.cardHeader}>
//             <h2 className={styles.cardTitle}>Edição de projeto - {projeto.titulo}</h2>
//           </div>
//           <div className={styles.cardContent}>
//             {getFieldError("general") && <div className={styles.errorMessage}>{getFieldError("general")}</div>}

//             {regioesError && <div className={styles.errorMessage}>Erro ao carregar regiões: {regioesError}</div>}

//             {successMessage && <div className={styles.successMessage}>{successMessage}</div>}

//             <form onSubmit={handleSubmit}>
//               <div className={styles.formGroup}>
//                 <label htmlFor="titulo" className={styles.label}>
//                   Título do projeto *
//                 </label>
//                 <input
//                   id="titulo"
//                   value={projetoEditado.titulo}
//                   onChange={(e) => handleInputChange("titulo", e.target.value)}
//                   className={`${styles.input} ${hasFieldError("titulo") ? styles.inputError : ""}`}
//                   placeholder="Digite o título do projeto"
//                 />
//                 {hasFieldError("titulo") && <span className={styles.fieldError}>{getFieldError("titulo")}</span>}
//               </div>

//               {/* Formato */}
//               <div className={styles.formGroup}>
//                 <label htmlFor="formato" className={styles.label}>
//                   Formato *
//                 </label>
//                 <select
//                   id="formato"
//                   value={projetoEditado.formato}
//                   onChange={(e) => handleInputChange("formato", e.target.value)}
//                   className={`${styles.select} ${hasFieldError("formato") ? styles.inputError : ""}`}
//                 >
//                   <option value="">Selecione o formato</option>
//                   {formatos.map((formato) => (
//                     <option key={formato} value={formato}>
//                       {formato}
//                     </option>
//                   ))}
//                 </select>
//                 {hasFieldError("formato") && (
//                   <span className={styles.fieldError}>{getFieldError("formato")}</span>
//                 )}
//               </div>

//               {/* Regiões */}
//               {!isRemoto && (
//                 <div className={styles.formGroup}>
//                   <label htmlFor="regiao" className={styles.label}>
//                     Região aceita *
//                   </label>
//                   {regioesLoading ? (
//                     <div className={styles.loadingText}>Carregando regiões...</div>
//                   ) : (
//                     <select
//                       id="regiao"
//                       value={projetoEditado.regioesAceitas[0] || ""}
//                       onChange={(e) => handleInputChange("regioesAceitas", e.target.value ? [e.target.value] : [])}
//                       className={`${styles.select} ${hasFieldError("regioesAceitas") ? styles.inputError : ""}`}
//                     >
//                       <option value="">Selecione uma região</option>
//                       {regioes.map((regiao) => (
//                         <option key={regiao.id} value={regiao.id.toString()}>
//                           {regiao.nome} ({regiao.abreviacao})
//                         </option>
//                       ))}
//                     </select>
//                   )}
//                   {hasFieldError("regioesAceitas") && (
//                     <span className={styles.fieldError}>{getFieldError("regioesAceitas")}</span>
//                   )}
//                 </div>
//               )}

//               {/* Estado, Cidade */}
//               {!isRemoto && (
//                 <div className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}>
//                   <div>
//                     <label htmlFor="estado" className={styles.label}>
//                       Estado *
//                     </label>
//                     <select
//                       id="estado"
//                       value={projetoEditado.estado}
//                       onChange={(e) => handleInputChange("estado", e.target.value)}
//                       className={`${styles.select} ${hasFieldError("estado") ? styles.inputError : ""}`}
//                       disabled={estadosLoading || projetoEditado.regioesAceitas.length === 0}
//                     >
//                       <option value="">
//                         {projetoEditado.regioesAceitas.length === 0
//                           ? "Selecione uma região primeiro"
//                           : estadosLoading
//                             ? "Carregando estados..."
//                             : "Selecione o estado"}
//                       </option>
//                       {estados.map((estado) => (
//                         <option key={estado.id} value={estado.id}>
//                           {estado.nome} ({estado.uf})
//                         </option>
//                       ))}
//                     </select>
//                     {hasFieldError("estado") && <span className={styles.fieldError}>{getFieldError("estado")}</span>}
//                     {estadosError && <span className={styles.fieldError}>{estadosError}</span>}
//                   </div>

//                   <div>
//                     <label htmlFor="cidade" className={styles.label}>
//                       Cidade *
//                     </label>
//                     <select
//                       id="cidade"
//                       value={projetoEditado.cidade}
//                       onChange={(e) => handleInputChange("cidade", e.target.value)}
//                       className={`${styles.select} ${hasFieldError("cidade") ? styles.inputError : ""}`}
//                       disabled={cidadesLoading || !projetoEditado.estado}
//                     >
//                       <option value="">
//                         {!projetoEditado.estado
//                           ? "Selecione um estado primeiro"
//                           : cidadesLoading
//                             ? "Carregando cidades..."
//                             : "Selecione a cidade"}
//                       </option>
//                       {cidades.map((cidade) => (
//                         <option key={cidade.id} value={cidade.id}>
//                           {cidade.nome}
//                         </option>
//                       ))}
//                     </select>
//                     {hasFieldError("cidade") && <span className={styles.fieldError}>{getFieldError("cidade")}</span>}
//                     {cidadesError && <span className={styles.fieldError}>{cidadesError}</span>}
//                   </div>
//                 </div>
//               )}

//               <div className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}>
//                 <div>
//                   <label htmlFor="instituicao" className={styles.label}>
//                     Instituição de pesquisa *
//                   </label>
//                   <input
//                     id="instituicao"
//                     value={projetoEditado.instituicao}
//                     onChange={(e) => handleInputChange("instituicao", e.target.value)}
//                     className={`${styles.input} ${hasFieldError("instituicao") ? styles.inputError : ""}`}
//                     placeholder="Digite a instituição de pesquisa"
//                   />
//                   {hasFieldError("instituicao") && (
//                     <span className={styles.fieldError}>{getFieldError("instituicao")}</span>
//                   )}
//                 </div>
//                 <div>
//                   <label htmlFor="vagas" className={styles.label}>
//                     Número de vagas *
//                   </label>
//                   <input
//                     id="vagas"
//                     type="number"
//                     min="1"
//                     value={projetoEditado.vagas}
//                     onChange={(e) => handleInputChange("vagas", Number.parseInt(e.target.value) || 0)}
//                     className={`${styles.input} ${hasFieldError("vagas") ? styles.inputError : ""}`}
//                     placeholder="20"
//                   />
//                   {hasFieldError("vagas") && <span className={styles.fieldError}>{getFieldError("vagas")}</span>}
//                 </div>
//               </div>

//               <div className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}>
//                 <div>
//                   <label htmlFor="dataInicio" className={styles.label}>
//                     Data de início *
//                   </label>
//                   <input
//                     id="dataInicio"
//                     type="date"
//                     value={projetoEditado.dataInicio}
//                     onChange={(e) => handleInputChange("dataInicio", e.target.value)}
//                     className={`${styles.input} ${hasFieldError("dataInicio") ? styles.inputError : ""}`}
//                   />
//                   {hasFieldError("dataInicio") && (
//                     <span className={styles.fieldError}>{getFieldError("dataInicio")}</span>
//                   )}
//                 </div>
//                 <div>
//                   <label htmlFor="dataFim" className={styles.label}>
//                     Data de fim *
//                   </label>
//                   <input
//                     id="dataFim"
//                     type="date"
//                     value={projetoEditado.dataFim}
//                     onChange={(e) => handleInputChange("dataFim", e.target.value)}
//                     className={`${styles.input} ${hasFieldError("dataFim") ? styles.inputError : ""}`}
//                   />
//                   {hasFieldError("dataFim") && <span className={styles.fieldError}>{getFieldError("dataFim")}</span>}
//                 </div>
//               </div>

//               <div className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}>
//                 <div>
//                   <label htmlFor="inicioInscricoes" className={styles.label}>
//                     Início das inscrições *
//                   </label>
//                   <input
//                     id="inicioInscricoes"
//                     type="date"
//                     value={projetoEditado.inicioInscricoes}
//                     onChange={(e) => handleInputChange("inicioInscricoes", e.target.value)}
//                     className={`${styles.input} ${hasFieldError("inicioInscricoes") ? styles.inputError : ""}`}
//                   />
//                   {hasFieldError("inicioInscricoes") && (
//                     <span className={styles.fieldError}>{getFieldError("inicioInscricoes")}</span>
//                   )}
//                 </div>
//                 <div>
//                   <label htmlFor="fimInscricoes" className={styles.label}>
//                     Fim das inscrições *
//                   </label>
//                   <input
//                     id="fimInscricoes"
//                     type="date"
//                     value={projetoEditado.fimInscricoes}
//                     onChange={(e) => handleInputChange("fimInscricoes", e.target.value)}
//                     className={`${styles.input} ${hasFieldError("fimInscricoes") ? styles.inputError : ""}`}
//                   />
//                   {hasFieldError("fimInscricoes") && (
//                     <span className={styles.fieldError}>{getFieldError("fimInscricoes")}</span>
//                   )}
//                 </div>
//               </div>

//               <div className={styles.formGroup}>
//                 <label htmlFor="tutorId" className={styles.label}>
//                   Tutor *
//                 </label>
//                 {tutoresError && (
//                   <div className={styles.errorMessage} style={{ marginBottom: "0.5rem", fontSize: "0.75rem" }}>
//                     {tutoresError}
//                     <button
//                       type="button"
//                       onClick={recarregarTutores}
//                       className={styles.retryButton}
//                       style={{ marginLeft: "0.5rem" }}
//                     >
//                       Tentar novamente
//                     </button>
//                   </div>
//                 )}
//                 <select
//                   id="tutorId"
//                   value={projetoEditado.tutorId}
//                   onChange={(e) => handleInputChange("tutorId", e.target.value)}
//                   className={`${styles.select} ${hasFieldError("tutorId") ? styles.inputError : ""}`}
//                   disabled={tutoresLoading}
//                 >
//                   <option value="">{tutoresLoading ? "Carregando tutores..." : "Selecione um tutor"}</option>
//                   {tutores.map((tutor) => (
//                     <option key={tutor.id} value={tutor.id}>
//                       {tutor.nome} - {tutor.email}
//                     </option>
//                   ))}
//                 </select>
//                 {hasFieldError("tutorId") && <span className={styles.fieldError}>{getFieldError("tutorId")}</span>}
//               </div>

//               <div className={styles.formGroup}>
//                 <label htmlFor="resumo" className={styles.label}>
//                   Descrição do projeto *
//                 </label>
//                 <textarea
//                   id="resumo"
//                   value={projetoEditado.resumo}
//                   onChange={(e) => handleInputChange("resumo", e.target.value)}
//                   className={`${styles.textarea} ${hasFieldError("resumo") ? styles.inputError : ""}`}
//                   placeholder="Digite a descrição detalhada do projeto"
//                 />
//                 {hasFieldError("resumo") && <span className={styles.fieldError}>{getFieldError("resumo")}</span>}
//               </div>

//               <div style={{ display: "flex", gap: "1rem", justifyContent: "space-between", alignItems: "center" }}>
//                 <div>
//                   <button
//                     type="button"
//                     onClick={() => setShowDeactivateConfirm(true)}
//                     style={{
//                       padding: "0.75rem 1.5rem",
//                       background: "#dc2626",
//                       border: "1px solid #dc2626",
//                       borderRadius: "0.375rem",
//                       color: "white",
//                       cursor: "pointer",
//                       fontSize: "0.875rem",
//                       fontWeight: "500",
//                       transition: "all 0.2s",
//                     }}
//                     onMouseOver={(e) => {
//                       e.currentTarget.style.background = "#b91c1c"
//                     }}
//                     onMouseOut={(e) => {
//                       e.currentTarget.style.background = "#dc2626"
//                     }}
//                     disabled={isLoading || isDeactivating}
//                   >
//                     Desativar Projeto
//                   </button>
//                 </div>

//                 <div style={{ display: "flex", gap: "1rem" }}>
//                   <button
//                     type="button"
//                     onClick={onVoltar}
//                     style={{
//                       padding: "0.75rem 1.5rem",
//                       background: "transparent",
//                       border: "1px solid #d1d5db",
//                       borderRadius: "0.375rem",
//                       color: "#374151",
//                       cursor: "pointer",
//                       fontSize: "0.875rem",
//                       fontWeight: "500",
//                       transition: "all 0.2s",
//                     }}
//                     onMouseOver={(e) => {
//                       e.currentTarget.style.background = "#f3f4f6"
//                     }}
//                     onMouseOut={(e) => {
//                       e.currentTarget.style.background = "transparent"
//                     }}
//                   >
//                     Cancelar
//                   </button>
//                   <button
//                     type="submit"
//                     className={styles.button}
//                     disabled={isLoading || regioesLoading || estadosLoading || tutoresLoading || isDeactivating}
//                     style={{ width: "auto", padding: "0.75rem 1.5rem" }}
//                   >
//                     {isLoading ? "Salvando..." : "Salvar Alterações"}
//                   </button>
//                 </div>
//               </div>
//             </form>
//             {/* Modal de confirmação de desativação */}
//             {showDeactivateConfirm && (
//               <div
//                 style={{
//                   position: "fixed",
//                   top: 0,
//                   left: 0,
//                   right: 0,
//                   bottom: 0,
//                   backgroundColor: "rgba(0, 0, 0, 0.5)",
//                   display: "flex",
//                   alignItems: "center",
//                   justifyContent: "center",
//                   zIndex: 1000,
//                 }}
//                 onClick={() => setShowDeactivateConfirm(false)}
//               >
//                 <div
//                   style={{
//                     backgroundColor: "white",
//                     borderRadius: "0.5rem",
//                     padding: "2rem",
//                     maxWidth: "400px",
//                     width: "90%",
//                     boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
//                   }}
//                   onClick={(e) => e.stopPropagation()}
//                 >
//                   <h3
//                     style={{
//                       fontSize: "1.125rem",
//                       fontWeight: "600",
//                       color: "#111827",
//                       marginBottom: "1rem",
//                     }}
//                   >
//                     Confirmar Desativação
//                   </h3>
//                   <p
//                     style={{
//                       color: "#6b7280",
//                       marginBottom: "1.5rem",
//                       lineHeight: "1.5",
//                     }}
//                   >
//                     Tem certeza que deseja desativar o projeto "{projeto.titulo}"? Esta ação pode ser revertida
//                     posteriormente.
//                   </p>
//                   <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end" }}>
//                     <button
//                       type="button"
//                       onClick={() => setShowDeactivateConfirm(false)}
//                       disabled={isDeactivating}
//                       style={{
//                         padding: "0.5rem 1rem",
//                         background: "transparent",
//                         border: "1px solid #d1d5db",
//                         borderRadius: "0.375rem",
//                         color: "#374151",
//                         cursor: "pointer",
//                         fontSize: "0.875rem",
//                         fontWeight: "500",
//                         transition: "all 0.2s",
//                       }}
//                       onMouseOver={(e) => {
//                         e.currentTarget.style.background = "#f3f4f6"
//                       }}
//                       onMouseOut={(e) => {
//                         e.currentTarget.style.background = "transparent"
//                       }}
//                     >
//                       Cancelar
//                     </button>
//                     <button
//                       type="button"
//                       onClick={handleDeactivate}
//                       disabled={isDeactivating}
//                       style={{
//                         padding: "0.5rem 1rem",
//                         background: "#dc2626",
//                         border: "1px solid #dc2626",
//                         borderRadius: "0.375rem",
//                         color: "white",
//                         cursor: "pointer",
//                         fontSize: "0.875rem",
//                         fontWeight: "500",
//                         transition: "all 0.2s",
//                       }}
//                       onMouseOver={(e) => {
//                         if (!isDeactivating) {
//                           e.currentTarget.style.background = "#b91c1c"
//                         }
//                       }}
//                       onMouseOut={(e) => {
//                         if (!isDeactivating) {
//                           e.currentTarget.style.background = "#dc2626"
//                         }
//                       }}
//                     >
//                       {isDeactivating ? "Desativando..." : "Desativar"}
//                     </button>
//                   </div>
//                 </div>
//               </div>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   )
// }
