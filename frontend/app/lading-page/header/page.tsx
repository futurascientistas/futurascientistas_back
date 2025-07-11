import { MessageCircle, Instagram, Facebook, Youtube } from "lucide-react"
import styles from "./header.module.css"
import { useRouter } from "next/navigation"

export default function Header() {
  const router = useRouter()
  
  return (
    <div>
    <header className={styles.header}>
      {/* Logo */}
      <div className={styles.logo}>
        <div className={styles.headerfc__logo}>
          <img src="/images/futuras-cientistas-logo-horizontal-white.png" alt="Futuras Cientistas" />
        </div>
      </div>

      {/* Social Icons and Buttons */}
      <div className={styles.rightSection}>
        {/* Social Media Icons */}
        <div className={styles.socialIcons}>
          <MessageCircle className={styles.socialIcon} />
          <Instagram className={styles.socialIcon} />
          <Facebook className={styles.socialIcon} />
          <Youtube className={styles.socialIcon} />
        </div>

        {/* Action Buttons */}
        <div className={styles.headerfc__actions}>
          <button className={styles.headerfc__btn} onClick={ () => { router.push('/login')}}>ENTRAR</button>
          <button className={`${styles.headerfc__btn} ${styles.headerfc__btn_secondary}`} onClick={ () => router.push("/register")}>INSCREVA-SE</button>
        </div>
      </div>
    </header>
    </div>
  )
}


// import React from "react";
// import styles from './header.module.css';
// import { useRouter } from "next/navigation"
// import { MessageCircle, Instagram, Facebook, Youtube } from "lucide-react"

// export default function Header() {
//   const router = useRouter()

//   return (
//     <header className={styles.headerfc}>
//       {/* Logo */}
//       <div className={styles.headerfc__logo}>
//         <img src="/images/futuras-cientistas-logo-horizontal-white.png" alt="Futuras Cientistas" />
//       </div>

//       <div className={styles.headerfc__container}>
//         {/* Redes sociais */}
//         <div className={styles.socialIcons}>
//           {/* Social Media Icons */}
//           <MessageCircle className={styles.socialIcon} />
//           <Instagram className={styles.socialIcon} />
//           <Facebook className={styles.socialIcon} />
//           <Youtube className={styles.socialIcon} />
//         </div>
//         {/* Botões */}
//         <div className={styles.headerfc__actions}>
//           <button className={styles.headerfc__btn} onClick={ () => { router.push('/login')}}>ENTRAR</button>
//           <button className={styles.headerfc__btn + " " + styles.headerfc__btn_secondary} onClick={ () => router.push("/register")}>INSCREVA-SE</button>
//         </div>
//       </div>
//     </header>
//   );
// }
