"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertCircle, ArrowLeft, CheckCircle2 } from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useAuth } from "@/hooks/auth-context"
import { recoverPassword } from "@/services/auth"

export default function PasswordRecoveryForm() {
  const { refreshUser } = useAuth()
  const [cpf, setCpf] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isSuccess, setIsSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)

    // Basic validation
    if (!cpf.trim()) {
      setErrorMessage("Informe o CPF para recuperação de senha.")
      return
    }

    // Recovery process
    setIsLoading(true)
    const result = await recoverPassword(cpf);
    if (result.success) {
      refreshUser(); // Atualiza o contexto após recuperação
      setIsSuccess(true)
    } else {
      setErrorMessage(result.message)
    }
    setIsLoading(false)
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
        <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-sm">
          <div className="mb-6">
            <Link href="/login" className="inline-flex items-center text-sm text-gray-600 hover:text-pink-500 mb-4">
              <ArrowLeft className="h-4 w-4 mr-1" />
              Voltar para o login
            </Link>
            <h1 className="text-2xl font-bold text-gray-800">Recuperação de senha</h1>
            <p className="text-sm text-gray-600 mt-1">Digite seu CPF para receber instruções de recuperação de senha</p>
          </div>

          {errorMessage && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          {isSuccess ? (
            <Alert className="mb-4 bg-green-50 border-green-200 text-green-800">
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              <AlertDescription>
                Instruções de recuperação de senha foram enviadas para o e-mail associado a este CPF.
              </AlertDescription>
            </Alert>
          ) : (
            <form className="space-y-4" onSubmit={handleSubmit}>
              <div>
                <Label htmlFor="cpf" className="text-sm font-medium">
                  CPF<span className="text-pink-500">*</span>
                </Label>
                <Input
                  id="cpf"
                  placeholder="000.000.000-00"
                  className="mt-1"
                  value={cpf}
                  onChange={(e) => setCpf(e.target.value)}
                  required
                />
              </div>

              <Button type="submit" className="w-full bg-pink-400 hover:bg-pink-500 text-white" disabled={isLoading}>
                {isLoading ? "Processando..." : "Recuperar senha"}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
