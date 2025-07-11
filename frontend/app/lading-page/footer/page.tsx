import styles from './footer.module.css';

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.topWave}></div>
      <div className={styles.content}>
        <div className={styles.columnLeft}>
          <div className={styles.footerLogo}>
            <img src="/images/futuras-cientistas-logo-horizontal-white.png" alt="Futuras Cientistas" />
          </div>

          <p className={styles.description}>
            Iniciativa nacional que promove o protagonismo de meninas no ensino médio por meio da ciência, da pesquisa e da equidade de gênero.<br />
            Juntas, construindo um futuro mais diverso, inclusivo e transformador.
          </p>
          <p className={styles.copyright}>
            © 2025 Programa Futuras Cientistas – Todos os direitos reservados.
          </p>
        </div>
        <div className={styles.columnGroup}>
          <div className={styles.column}>
            <span className={styles.colTitle}>Programa</span>
            <a href="#" className={styles.link}>Contato da Organização</a>
            <a href="#" className={styles.link}>FAQ</a>
            <a href="#" className={styles.link}>Requisitos para Participar</a>
          </div>
          <div className={styles.column}>
            <span className={styles.colTitle}>Informações</span>
            <a href="#" className={styles.link}>Política de Privacidade</a>
            <a href="#" className={styles.link}>Termos de Uso</a>
            <a href="#" className={styles.link}>Acessibilidade Digital</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
