import { BookOpen } from 'lucide-react';
import styles from './programmodules.module.css';

export default function ProgramModules() {
  return (
    <section className={styles.section}>
      <h2 className={styles.title}>Módulos do Programa</h2>
      <p className={styles.subtitle}>
        Conheça mais dos módulos e oportunidades que o programa pode oferecer
      </p>

      <div className={styles.modules}>
        <div className={styles.card}>
          <h3 className={styles.cardTitle}>Imersão Científica</h3>
          <span className={styles.cardSubtitle}>Módulo 1</span>
          <p className={styles.cardText}>
            Se você é aluna da 2ª série do EM ou professora da rede pública estadual, participe da Imersão Científica! Durante janeiro, você vivencia a rotina de pesquisa em universidades e empresas. São 470 vagas com atividades presenciais ou remotas, em projetos incríveis na área STEM.
          </p>
        </div>
        <div className={styles.card}>
          <h3 className={styles.cardTitle}>Banca de Estudos</h3>
          <span className={styles.cardSubtitle}>Módulo 2</span>
          <p className={styles.cardText}>
            Aluna da 3ª série do Ensino Médio da rede pública estadual? Aqui você se prepara pro ENEM com aulas online de exatas e redação, além de apoio psicológico. São 100 vagas para um curso intensivo que acontece entre setembro e outubro. Tudo de forma totalmente gratuita!
          </p>
        </div>
        <div className={styles.card}>
          <h3 className={styles.cardTitle}>Mentorias</h3>
          <span className={styles.cardSubtitle}>Módulo 3</span>
          <p className={styles.cardText}>
            Já participou do programa e entrou na universidade? Agora é hora de seguir conectada! O módulo de Mentorias, em parceria com a Alumna, oferece apoio com profissionais experientes e vagas exclusivas. Uma rede colaborativa feita pra você seguir crescendo no mundo STEM.
          </p>
        </div>
      </div>

      <div className={styles.opportunities}>
        
        <div className={styles.iconWrapper}>
          <BookOpen color="white" size={48} strokeWidth={2.5} />
        </div>
        
        <div>
          <h3 className={styles.oppTitle}>Estágios e Oportunidades</h3>
          <p className={styles.oppText}>
            Ao ingressar na universidade, buscamos conectar nossas participantes a estágios, bolsas de iniciação ou pesquisa nas áreas STEM. Essa etapa amplia a vivência profissional e científica, fortalecendo o vínculo com o mercado e a continuidade na carreira acadêmica.
          </p>
        </div>
      </div>
    </section>
  );
}
