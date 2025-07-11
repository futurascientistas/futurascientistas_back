"use client"

import { useState, useEffect } from "react"
import {
  User,
  Plus,
  TrendingUp,
  Calendar,
  Award,
  FileText,
  ChevronLeft,
  ChevronRight,
  X,
  Menu,
  Bell,
  BarChart3,
  Database,
  LogOut,
  FolderOpen,
} from "lucide-react"
import styles from "./sidebar.module.css"
import { useAuth } from "@/hooks/auth-context"
import { useRouter } from "next/navigation"

interface SidebarProps {
  activeItem: string
  onItemClick: (item: string) => void
}

export default function SidebarItems({ activeItem, onItemClick }: SidebarProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const [isMobile, setIsMobile] = useState(false)
  const { user, logout, refreshUser, loading } = useAuth()
  const router = useRouter()

  

  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth <= 768
      setIsMobile(mobile)
      if (mobile) {
        setIsExpanded(false) // Sidebar fechado por padrão no mobile
      } else {
        setIsExpanded(true) // Sidebar aberto por padrão no desktop
      }
    }

    checkMobile()
    window.addEventListener("resize", checkMobile)
    return () => window.removeEventListener("resize", checkMobile)
  }, [])

  // Atualizar CSS custom properties para controlar o layout
  useEffect(() => {
    const root = document.documentElement
    if (isMobile) {
      root.style.setProperty("--sidebar-width", "0px")
    } else {
      root.style.setProperty("--sidebar-width", isExpanded ? "280px" : "70px")
    }
  }, [isExpanded, isMobile])

  if(!user || loading) {
    return null;
  }

  const menuItems = [
    // {
    //   id: "perfil",
    //   title: "Perfil",
    //   icon: <User className={styles.menuIcon} />,
    //   roles: ["estudante"], //"admin", "estudante", "tutor"
    //   path: "/dashboard/minha-conta",
    // },
    {
      id: "cadastro",
      title: "Criar projeto",
      icon: <Plus className={styles.menuIcon} />,
      roles: ["admin", "tutor"],
      path: "/project",
    },
    {
      id: "lista_projetos",
      title: "Lista de Projetos",
      icon: <FileText className={styles.menuIcon} />,
      roles: ["admin", "tutor"],
      path: "/project-list",
    },
    {
      id: "inscricao_aluna",
      title: "Minha Inscrição",
      icon: <User className={styles.menuIcon} />,
      roles: ["estudante"], //, "tutor", "estudante"
      path: "/inscricao-aluna",
    },
    {
      id: "projetos_disponiveis",
      title: "Projetos Disponíveis",
      icon: <FolderOpen className={styles.menuIcon} />,
      roles: ["estudante"],
      path: "/projetos-disponiveis",
    },
    {
      id: "cronograma",
      title: "Cronograma",
      icon: <Calendar className={styles.menuIcon} />,
      roles: [], // "admin", "tutor", "estudante"
      path: "/dashboard/cronograma",  
    },
    {
      id: "avaliacao",
      title: "Avaliação de inscrição",
      icon: <Award className={styles.menuIcon} />,
      roles: ["admin"], //, "tutor", "estudante"
      path: "/dashboard/avaliacao",
    },
    {
      id: "notificacoes",
      title: "Notificações",
      icon: <Bell className={styles.menuIcon} />,
      roles: [], // "admin", "tutor", "estudante"
      path: "/dashboard/notificacoes",
    },
    {
      id: "frequencia",
      title: "Frequência",
      icon: <BarChart3 className={styles.menuIcon} />,
      roles: [], // "admin", "tutor"
      path: "/dashboard/frequencia",
    },
    {
      id: "indicadores",
      title: "Indicadores",
      icon: <TrendingUp className={styles.menuIcon} />,
      roles: [], // "admin", "tutor"
      path: "/dashboard/indicadores",
    },
    {
      id: "analise",
      title: "Análise de relatórios (TCC)",
      icon: <FileText className={styles.menuIcon} />,
      roles: [], // "admin", "tutor"
      path: "/dashboard/analise",
    },
    {
      id: "dados",
      title: "Dados de projetos",
      icon: <Database className={styles.menuIcon} />,
      roles: ["admin", "tutor"],
      path: "/dashboard/dados",
    },
  ]

  const toggleSidebar = () => {
    setIsExpanded(!isExpanded)
  }

  const handleOverlayClick = () => {
    if (isMobile) {
      setIsExpanded(false)
    }
  }

  const handleLogout = async() => {
    // e.preventDefault()
    await logout()
    await refreshUser()
    router.push("/login")
  }

  const handleMenuItemClick = (itemId: string) => {
    const item = menuItems.find((i) => i.id === itemId);
    onItemClick(itemId)
    
    if (item?.path) {
      router.push(item.path);
    }

    if (itemId === "logout") {
      // lógica de logout
      handleLogout();
    }
    
    // Fechar sidebar no mobile após clicar em um item
    if (isMobile) {
      setIsExpanded(false)
    }
  }

  const getToggleIcon = () => {
    if (isMobile) {
      return <X size={14} />
    }
    return isExpanded ? <ChevronLeft size={14} /> : <ChevronRight size={14} />
  }

  const getMobileToggleClass = () => {
    if (!isMobile) return styles.mobileToggleHidden
    return isExpanded ? styles.mobileToggleHidden : styles.mobileToggleVisible
  }

  const getToggleAriaLabel = () => {
    if (isMobile) {
      return isExpanded ? "Fechar menu" : "Abrir menu"
    }
    return isExpanded ? "Contrair sidebar" : "Expandir sidebar"
  }

  return (
    <>
      {/* Overlay para mobile */}
      <div
        className={`${styles.overlay} ${isMobile && isExpanded ? styles.overlayVisible : ""}`}
        onClick={handleOverlayClick}
      />

      {/* Botão hambúrguer fixo para mobile quando sidebar está fechado */}
      <button
        type="button"
        className={`${styles.mobileToggle} ${getMobileToggleClass()}`}
        onClick={toggleSidebar}
        aria-label="Abrir menu de navegação"
      >
        <Menu size={20} />
      </button>

      {/* Sidebar */}
      <div className={`${styles.sidebar} ${isExpanded ? styles.sidebarExpanded : styles.sidebarCollapsed}`}>
        {/* Header do sidebar com botão de toggle */}
        <div className={styles.sidebarHeader}>
          <button
            type="button"
            className={styles.toggleButton}
            onClick={toggleSidebar}
            aria-label={getToggleAriaLabel()}
          >
            {getToggleIcon()}
          </button>
        </div>

        {/* Menu items */}
        <ul className={styles.menuList}>
          {menuItems
          .filter((item) => !user || item.roles.includes(user.role))
          .map((item) => (
            <li
              key={item.id}
              className={`${styles.menuItem} ${activeItem === item.id ? styles.active : ""}`}
              onClick={() => handleMenuItemClick(item.id)}
            >
              {item.icon}
              <span className={styles.menuText}>{item.title}</span>
            </li>
          ))}

          {/* Item Sair no final */}
          <li className={`${styles.menuItem} ${styles.menuItemLogout}`} onClick={() => handleMenuItemClick("logout")}>
            <LogOut className={styles.menuIcon} />
            <span className={styles.menuText}>Sair</span>
          </li>
        </ul>
      </div>
    </>
  )
}
