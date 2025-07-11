"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertCircle, CheckCircle2, Eye, EyeOff, Info } from "lucide-react"
import Image from "next/image"
import { useRouter } from "next/navigation"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useAuth } from "@/hooks/auth-context"
import { resetPassword } from "./services/auth"


export default function PasswordResetForm() {
  const { refreshUser } = useAuth()
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [passwordStrength, setPasswordStrength] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const router = useRouter()

  const calculatePasswordStrength = (password: string) => {
    if (!password) return 0

    // Password strength calculation
    let strength = 0
    if (password.length > 6) strength += 1
    if (password.length > 10) strength += 1
    if (/[A-Z]/.test(password)) strength += 1
    if (/[0-9]/.test(password)) strength += 1
    if (/[^A-Za-z0-9]/.test(password)) strength += 1

    return Math.min(strength, 4)
  }

  const getPasswordStrengthText = (strength: number) => {
    switch (strength) {
      case 0:
        return "Muito fraca"
      case 1:
        return "Fraca"
      case 2:
        return "Média"
      case 3:
        return "Forte"
      case 4:
        return "Muito forte"
      default:
        return ""
    }
  }

  const getPasswordStrengthColor = (strength: number) => {
    switch (strength) {
      case 0:
        return "bg-gray-200"
      case 1:
        return "bg-red-500"
      case 2:
        return "bg-orange-500"
      case 3:
        return "bg-yellow-500"
      case 4:
        return "bg-green-500"
      default:
        return "bg-gray-200"
    }
  }

  const handleNewPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setNewPassword(value)
    setPasswordStrength(calculatePasswordStrength(value))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)
    setSuccessMessage(null)

    // Validation
    if (!newPassword) {
      setErrorMessage("A nova senha é obrigatória")
      return
    }

    if (passwordStrength < 2) {
      setErrorMessage("A nova senha é muito fraca. Escolha uma senha mais forte.")
      return
    }

    if (newPassword !== confirmPassword) {
      setErrorMessage("A nova senha e a confirmação não coincidem")
      return
    }

    setIsLoading(true)

    // Password reset process
    const result = await resetPassword(newPassword)

    if (!result.success) {
      setErrorMessage(result.message)
      setIsLoading(false)
      return
    } else {
      setSuccessMessage("Senha redefinida com sucesso!")
      setTimeout(() => {
        setIsLoading(false)
        refreshUser() // Atualiza o contexto após redefinição da senha
        router.push("/login")
      }, 1500)
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-purple-700 p-4">
      <div className="container mx-auto flex justify-between items-center py-4">
        <div className="w-40">
          <Image
            src="/images/futuras-cientistas-logo.png"
            alt="Futuras Cientistas"
            width={160}
            height={50}
            className="w-full h-auto"
          />
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-800">Redefinir sua senha</h1>
            <p className="text-sm text-gray-600 mt-1">
              Por motivos de segurança, você precisa criar uma nova senha para continuar.
            </p>
          </div>

          <Alert className="mb-6 bg-blue-50 border-blue-200 text-blue-800">
            <Info className="h-4 w-4 text-blue-500" />
            <AlertDescription>
              Sua senha deve ter pelo menos 8 caracteres e incluir letras maiúsculas, números e caracteres especiais.
            </AlertDescription>
          </Alert>

          {errorMessage && (
            <Alert variant="destructive" className="mb-6">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          {successMessage && (
            <Alert className="mb-6 bg-green-50 border-green-200 text-green-800">
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              <AlertDescription>{successMessage}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="new-password" className="text-sm font-medium">
                Nova senha<span className="text-pink-500">*</span>
              </Label>
              <div className="relative mt-1">
                <Input
                  id="new-password"
                  type={showNewPassword ? "text" : "password"}
                  value={newPassword}
                  onChange={handleNewPasswordChange}
                  required
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                >
                  {showNewPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
              <div className="mt-2">
                <div className="h-1 flex space-x-1">
                  <div
                    className={`flex-1 ${passwordStrength >= 1 ? getPasswordStrengthColor(1) : "bg-gray-200"}`}
                  ></div>
                  <div
                    className={`flex-1 ${passwordStrength >= 2 ? getPasswordStrengthColor(2) : "bg-gray-200"}`}
                  ></div>
                  <div
                    className={`flex-1 ${passwordStrength >= 3 ? getPasswordStrengthColor(3) : "bg-gray-200"}`}
                  ></div>
                  <div
                    className={`flex-1 ${passwordStrength >= 4 ? getPasswordStrengthColor(4) : "bg-gray-200"}`}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Força da senha: <span className="font-medium">{getPasswordStrengthText(passwordStrength)}</span>
                </p>
              </div>
            </div>

            <div>
              <Label htmlFor="confirm-password" className="text-sm font-medium">
                Confirmar nova senha<span className="text-pink-500">*</span>
              </Label>
              <div className="relative mt-1">
                <Input
                  id="confirm-password"
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <Button type="submit" className="w-full bg-pink-400 hover:bg-pink-500 text-white" disabled={isLoading}>
              {isLoading ? "Redefinindo..." : "Redefinir senha"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
