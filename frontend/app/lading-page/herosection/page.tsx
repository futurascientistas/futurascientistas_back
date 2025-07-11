import styles from './herosection.module.css';

export default function HeroSection() {
  return (
    <section className={styles.heroSection}>
      <h1 className={styles.title}>
        Inspire <span className={styles.underline}>meninas</span> a transformar o futuro pela ciência
      </h1>
      <p className={styles.subtitle}>
        O programa Futuras Cientistas conecta alunas do ensino médio à pesquisa científica por meio<br />
        de experiências práticas, mentoria e formação cidadã.
      </p>
    </section>
  );
}
