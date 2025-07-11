'use client';
import { useProjects } from '@/hooks/use-projects';
import { useRegioes } from '@/hooks/use-regioes';
import { useEstados } from '@/hooks/use-estados';
import { useCidades } from '@/hooks/use-cidades';
import { Project } from '@/types/project';
import { useEffect, useState } from 'react';
import styles from "./projectform.module.css";
import { FormValidator, ValidationError } from './form-validation';
import { useRouter } from "next/navigation";
import UserAutocomplete from '@/components/user-autocomplete/user-autocomplete';
import SuccessModal from '@/components/sucess-modal/sucess-modal';


const projetoDefault: Project = {
  id: "",
  nome: "",
  regiao: null,
  estado: null,
  cidade: null,
  formato: "",
  instituicao: "",
  descricao: "",
  vagas: 5,
  dataInicio: "",
  dataFim: "",
  inicioInscricoes: "",
  fimInscricoes: "",
  regioesAceitas: [],
  tutor: null,
  criadoPor: '',
  atualizadoPor: '',
  ehRemoto: false,
  status: '',
  ativo: false,
  criadoEm: '',
  atualizadoEm: '',
  estadosAceitos: [],
  cidadesAceitas: []
};

export default function ProjetosPage() {
  // Form controls
  const [isRemoto, setIsRemoto] = useState(false);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState(false)
  const [projeto, setProjeto] = useState(projetoDefault);
  const router = useRouter();

  // Hooks para carregamento de dados
  const { projetos, criarProjeto, isLoading, error: projectError, success: projectSuccess } = useProjects();
  const { regioes, isLoading: regioesLoading, error: regioesError } = useRegioes();
  const { estados: estadosDefault, filtrarEstadosPorRegiao, isLoading: estadosLoading } = useEstados();
  const { cidades, isLoading: cidadesLoading } = useCidades(projeto.estado ? projeto.estado.uf || "" : "");

  // Estados
  const [estados, setEstados] = useState(estadosDefault);
  
  // Formato de projeto
  const formatos = ["Presencial", "Remoto"];

  // Form Messages
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [successMessage, setSuccessMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationErrors = FormValidator.validateProject(projeto)
    if (validationErrors.length > 0) {
      setErrors(validationErrors)
      return;
    }

    setErrors([])
    await criarProjeto(projeto);
  };

  const handleInputChange = (field: keyof Project, value: any) => {
    if(field === "estado") {
      const estadoSelecionado = estados?.find((estado) => estado.id === value);
      setProjeto((prev) => ({ ...prev, [field]: estadoSelecionado, cidade: null })); // limpa cidade ao mudar estado

    } else if (field === "cidade") {
      const cidadeSelecionada = cidades?.find((cidade) => cidade.id === value);
      setProjeto((prev) => ({ ...prev, [field]: cidadeSelecionada }));

    } else if(field === "regiao") {
      const regiaoSelecionada = regioes?.find((regiao) => regiao.id === value);
      setProjeto((prev) => ({ ...prev, [field]: regiaoSelecionada, estado: null, cidade: null })); // limpa estado e cidade ao mudar região

      // Atualiza estados com base na região selecionada
      const estadosFiltrados = filtrarEstadosPorRegiao(value);
      setEstados(estadosFiltrados); 

    } else if(field === "formato") {
      setIsRemoto(value === "Remoto");
      setProjeto((prev) => ({ ...prev, [field]: value }));

    }else {
      setProjeto((prev) => ({ ...prev, [field]: value }));
    }

    if (errors.length > 0) {
      setErrors((prev) => prev.filter((error) => error.field !== field))
    }
  };

  const handleUserChange = (tutor: any) => {
    setProjeto((prev) => ({
      ...prev,
      tutor: tutor,
    }))
    console.log("Tutor selecionado:", tutor);

    if (errors.length > 0) {
      setErrors((prev) => prev.filter((error) => error.field !== "tutorId"))
    }

  }

  const getFieldError = (fieldName: string) => {
    var result = FormValidator.getFieldError(errors, fieldName);
    return result;
  };

  const hasFieldError = (fieldName: string) => {
    return !!getFieldError(fieldName);
  };

  useEffect(() => {
    if(projectSuccess) {
      setIsSuccessModalOpen(true)
      const timer = setTimeout(() => {
        router.push("/project-list");
        setIsSuccessModalOpen(false)
      }, 3000);

      return () => clearTimeout(timer);
    }
  })

  return (
    <div className={styles.container}>
      <div className={styles.contentWrapper}> 
        <div className={`${styles.card} ${styles.spacer}`}>
          {/* Card Header */}
          <div className={styles.cardHeader}>
            <h2 className={styles.cardTitle}>Cadastrar Novo Projeto</h2>
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
                  onChange={(e) => handleInputChange("formato", e.target.value)}
                  className={`${styles.select} ${hasFieldError("formato") ? styles.inputError : "" }`}
                >
                  <option value="">Selecione o formato</option>
                  {formatos.map((formato) => (
                    <option key={formato} value={formato}> {formato} </option>
                  ))}
                </select>
                {hasFieldError("formato") && (
                  <span className={styles.fieldError}> {getFieldError("formato")} </span>
                )}
              </div>


              {!isRemoto && (
                <div>
                  {/* Regiões */}
                  <div className={styles.formGroup}>
                    <label htmlFor="regiao" className={styles.label}>Região <span className={styles.mandatory}>*</span></label>
                    <select
                      id="regiao"
                      value={projeto.regiao?.id || ""}
                      onChange={(e) => handleInputChange("regiao", Number(e.target.value))}
                      className={`${styles.select} ${hasFieldError("regiao") ? styles.inputError : "" }`}
                      disabled={regioesLoading}
                    >
                      <option value={0}>Selecione a região</option>
                      {regioes.map((regiao) => (
                        <option key={regiao.id} value={regiao.id.toString()}>
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

                  {/* Estados e Cidades */}
                  <div className={`${styles.grid} ${styles.gridCols2} ${styles.formGroup}`}>
                    {/* Estados */}
                    <div className={styles.formGroup}>
                      <label htmlFor="estado" className={styles.label}>Estado <span className={styles.mandatory}>*</span></label>
                      <select
                        id="estado"
                        value={projeto.estado?.id || ""}
                        onChange={(e) => handleInputChange("estado", Number(e.target.value))}
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
                        onChange={(e) => handleInputChange("cidade", Number(e.target.value))}
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
                <label htmlFor="tutor" className={styles.label}>Tutor <span className={styles.mandatory}>*</span></label>
                <UserAutocomplete
                  groupName='tutor' 
                  value={""} 
                  onChange={ handleUserChange } />
                  {hasFieldError("tutor") && <span className={styles.fieldError}>{getFieldError("tutor")}</span>}
              </div>

              {/* Descrição do Projeto */}
              <div className={styles.formGroup}>
                <label htmlFor="resumo" className={styles.label}>Descrição do projeto <span className={styles.mandatory}>*</span></label>
                <textarea
                  id="resumo"
                  value={projeto.descricao}
                  onChange={(e) => handleInputChange("descricao", e.target.value)}
                  className={`${styles.textarea} ${hasFieldError("descricao") ? styles.inputError : "" }`}
                  placeholder="Digite a descrição detalhada do projeto"
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
                {isLoading ? "Salvando..." : "Salvar projeto"}
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

    // <div>
    //   <h1>Projetos</h1>
    //   <form onSubmit={handleSubmit}>
    //     <input value={projeto.nome} onChange={(e) => handleInputChange("nome", e.target.value)} placeholder="Título" required />
    //     <input value={projeto.descricao} onChange={(e) => handleInputChange("descricao", e.target.value)} placeholder="Descrição" required />
    //     <input type="number" value={projeto.vagas} onChange={(e) => handleInputChange("vagas", Number(e.target.value))} placeholder="Vagas" required />
    //     <input type="date" value={projeto.dataInicio} onChange={(e) => handleInputChange("dataInicio", e.target.value)} required />
    //     <input type="date" value={projeto.dataFim} onChange={(e) => handleInputChange("dataFim", e.target.value)} required />

    //     <select value={projeto.estado?.id || 0} onChange={(e) => handleInputChange("estado", Number(e.target.value))} required>
    //       <option value={0}>Selecione o Estado</option>
    //       {estados?.map((estado) => (
    //         <option key={estado.id} value={estado.id}>{estado.nome}</option>
    //       ))}
    //     </select>

    //     <select value={projeto.cidade?.id || 0} onChange={(e) => { handleInputChange("cidade", Number(e.target.value)); }} required disabled={!projeto.estado}>
    //       <option value={0}>Selecione a Cidade</option>
    //       {cidades?.map((cidade) => (
    //         <option key={cidade.id} value={cidade.id}>{cidade.nome}</option>
    //       ))}
    //     </select>

    //     <button type="submit">Criar Projeto</button>
    //   </form>

    //   {/* { projetos.length > 0 && (
    //     <div>${JSON.stringify(projetos)}
    //       <h2>Lista de Projetos:</h2>
    //     <ul>
    //       {projetos.map((p) => (
    //         <li key={p.id}>{p.nome} - {p.vagas} vagas</li>
    //       ))}
    //     </ul>
    //     </div>
    //   )} */}
      
    // </div>
  );
}
