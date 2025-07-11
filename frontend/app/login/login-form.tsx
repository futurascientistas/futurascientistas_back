"use client"

import type React from "react"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Eye, EyeOff, Facebook, Instagram, User, PhoneIcon as WhatsApp, Youtube, AlertCircle, KeyRound } from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import { useAuth } from "@/hooks/auth-context"
import { useRouter } from "next/navigation"
import { login } from "@/services/auth"
import styles from "./login.module.css"


export default function LoginForm() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  // const [selectedRole, setSelectedRole] = useState("estudante")
  const [cpf, setCpf] = useState('')
  const [senha, setSenha] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const { user, loading, refreshUser } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)

    // CPF e senha são obrigatórios
    if (!cpf.trim() || !senha.trim()) {
      setErrorMessage("Preencha o CPF e a senha.")
      return
    }

    // Página de login carregando
    setIsLoading(true)
    const result = await login(cpf, senha);

    // Verifica se o login foi bem-sucedido
    if (result.success) {
      refreshUser(); // Atualiza o contexto após login
      setIsLoading(false);

      router.push("/redirect");
    } else {
      setErrorMessage(result.message);
      setIsLoading(false);
    }
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <a className={styles.logoLink} href="/lading-page">
          <Image
            src="/images/futuras-cientistas-logo.png"
            alt="Futuras Cientistas"
            width={160}
            height={50}
            style={{ width: '100%', height: 'auto' }}
          />
        </a>
        <div className={styles.socialLinks}>
          <Link href="#" aria-label="WhatsApp"><WhatsApp style={{ width: 20, height: 20 }} /></Link>
          <Link href="#" aria-label="Instagram"><Instagram style={{ width: 20, height: 20 }} /></Link>
          <Link href="#" aria-label="Facebook"><Facebook style={{ width: 20, height: 20 }} /></Link>
          <Link href="#" aria-label="Youtube"><Youtube style={{ width: 20, height: 20 }} /></Link>
        </div>
      </div>

      <div className={styles.mainContent}>
        <div className={styles.card}>
          {errorMessage && (
            <Alert variant="destructive" className={styles.mb4}>
              <AlertCircle style={{ width: 16, height: 16 }} />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          
          <div className={styles.mb6}>
            {/*<Select defaultValue={selectedRole} onValueChange={setSelectedRole}>
              <SelectTrigger style={{ width: '100%' }}>
                <SelectValue placeholder="Selecione" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="estudante">Aluno (a)</SelectItem>
                <SelectItem value="professor">Professor (a)</SelectItem>
                <SelectItem value="tutor">Tutor (a)</SelectItem>
                <SelectItem value="admin">Equipe Futuras</SelectItem>
              </SelectContent>
            </Select>*/}
          </div>
          

          <form className={styles.form} onSubmit={handleSubmit}>
            <div className={styles.relative}>
              <div className={styles.inputIcon}>
                <User style={{ width: 20, height: 20 }} />
              </div>
              <Input
                type="text"
                placeholder="000.000.000-00"
                className={styles.inputField}
                onChange={(e) => setCpf(e.target.value)}
              />
            </div>

            <div className={styles.relative}>
              <div className={styles.inputIcon}>
                <KeyRound style={{ width: 20, height: 20 }} />
                <div style={{ width: 20, height: 20, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  
                </div>
              </div>
              <Input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••••"
                className={styles.inputField}
                onChange={(e) => setSenha(e.target.value)}
              />
              <button
                type="button"
                className={styles.eyeButton}
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
              >
                {showPassword ? <EyeOff style={{ width: 20, height: 20 }} /> : <Eye style={{ width: 20, height: 20 }} />}
              </button>
            </div>

            <div className={styles.forgot}>
              <Link href="/recuperar-senha" className={styles.forgotLink}>
                Esqueceu a senha?
              </Link>
            </div>

            <button
              type="submit"
              className={styles.button}
              disabled={isLoading}
            >
              {isLoading ? "Entrando..." : "Login"}
            </button>

            <div className={styles.textCenter}>
              Não tem cadastro?{" "}
              <Link href="/register" className={styles.registerLink}>
                Cadastre-se
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
