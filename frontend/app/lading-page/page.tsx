"use client";
import Footer from "./footer/page";
import ProgramModules from "./program-modules/page";
import Header from "./header/page";
import HeroSection from "./herosection/page";
import styles from "./landingpage.module.css";

export default function Home() {
  return (
    <div className={styles.raleway}>
      <Header />
      <HeroSection />
      <div className={styles.wrapper}>
        <div className={styles.topCircle}>
          <div className={styles.mapBox}>
            <img
              className={styles.map}
              src="/images/brasil.png"
              alt="Mapa do Brasil em roxo"
            />
          </div>

          <div className={styles.secondSection}>
            {/* Container Pink */}
            <div className={styles.pinkTitle}>Conheça mais o Programa</div>
            <div className={styles.containerPink}>
              {/* Row with 2 columns */}
              <div className={styles.contentPink}>
                {/* Content text - pink box */}
                <div className={styles.contentText1}>
                  O Futura Cientistas é um programa do Centro de Tecnologias
                  Estratégicas do Nordeste (Cetene) que estimula o contato de
                  alunas e professoras da rede pública de ensino com as áreas de
                  Ciência, Tecnologia, Engenharia e Matemática; a fim de
                  contribuir com a equidade de gênero no mercado profissional.
                </div>

                {/* Image - Gink Box */}
                <div className={styles.imageContainerPink}>
                  <div className={styles.circleImg1}></div>
                  <img
                    className={styles.contentImg1}
                    src="/images/menina_real.png"
                    alt="Futura Cientista"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* Component to fill in the blank space between the pink and green sections */}
        <div className={styles.pink}></div>

        {/* Green section */}
        <div className={styles.verde}>
          <div className={styles.containerGreen}>
            <div className={styles.contentGreen}>
              {/* Image - Green box */}
              <div className={styles.imageContainerGreen}>
                <div className={styles.circleImg2}></div>
                <img
                  className={styles.contentImg2}
                  src="/images/menina_oculos.png"
                  alt="Futura Cientista"
                />
              </div>

              {/* Content text - green box */}
              <div className={styles.contentText2}>
                Com o desenvolvimento do pensamento e de atividades científicas
                transdisciplinares, reduzimos barreiras para o acesso e
                permanência de meninas e mulheres nos espaços científicos. Em 10
                anos, 70% das participantes do programa foram aprovadas no
                vestibular. Destas, 80% escolheram cursos nas áreas de Ciência e
                Tecnologia. As frentes de atuação têm início no ensino médio,
                entretanto seguem até o ensino superior. 
              </div>
            </div>
          </div>
        </div>

        {/* Blue section */}
        <div className={styles.azul}>
          <div className={styles.containerBlue}>
            <div className={styles.contentBlue}>
              {/* Content text - blue box */}
              <div className={styles.contentText3}>
                OBJETIVO: Estimular o interesse e promover a participação de
                mulheres professoras e estudantes do ensino médio, nas áreas de
                Ciência e Tecnologia, através de sua aproximação a centros
                tecnológicos e instituições de ensino e pesquisa.
              </div>

              {/* Image - Blue box */}
              <div className={styles.imageContainerBlue}>
                <div className={styles.circleImg3}></div>
                <img
                  className={styles.contentImg3}
                  src="/images/professora.png"
                  alt="Futura Cientista"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      <ProgramModules />
      <Footer />
    </div>
  );
}
