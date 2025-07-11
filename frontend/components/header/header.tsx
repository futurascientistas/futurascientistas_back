"use client";

import Image from "next/image";
import Link from "next/link";
import { User } from "lucide-react";
import styles from "./header.module.css";
import { useAuth } from "@/hooks/auth-context"
import Router from "../router";

export default function Header() {
  const { user } = useAuth();
  
  return (
    <header className={styles.header}>
      <div className={styles.logo}>
        <Link href="/redirect">
            <Image
                src="/images/futuras-cientistas-logo-horizontal-white.png"
                alt="Futuras Cientistas"
                width={140}
                height={40}
            />
        </Link>
      </div>

      <div className={styles.userInfo}>
        <Link href="/dashboard/minha-conta">
          <div className={styles.userInfoTable}>
            <div>
              <div className={styles.userName}>{user.nome}</div>
            </div>
            <div className={styles.userAvatar}>
              <User size={16} />
            </div>
          </div>
        </Link>
      </div>
    </header>
  );
}
