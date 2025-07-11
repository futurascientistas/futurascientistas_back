"use client";

import type React from "react";

import { useState } from "react";
import { useAuth } from "@/hooks/auth-context";
import { useRouter } from "next/navigation";
import { register } from "@/services/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ArrowRight, AlertCircle, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import GroupSelect from "./components/group-select";

export default function RegistrationForm() {
  const [password, setPassword] = useState("");
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [nome, setNome] = useState("");
  const [cpf, setCpf] = useState("");
  const [cpfError, setCpfError] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [emailError, setEmailError] = useState<string | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<string | undefined>(
    undefined
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false)
  const { user, loading, refreshUser } = useAuth();
  const router = useRouter();

  const calculatePasswordStrength = (password: string) => {
    if (!password) return 0;

    // Simple password strength calculation
    let strength = 0;
    if (password.length > 6) strength += 1;
    if (password.length > 10) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;

    return Math.min(strength, 4);
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    setPasswordStrength(calculatePasswordStrength(newPassword));
  };

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      setEmailError("O email é obrigatório");
      return false;
    } else if (!emailRegex.test(email)) {
      setEmailError("Formato de email inválido");
      return false;
    } else {
      setEmailError(null);
      return true;
    }
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value;
    setEmail(newEmail);
    validateEmail(newEmail);
  };

  const validateCPF = (cpf: string) => {
    // Check if CPF is empty
    if (!cpf) {
      setCpfError("O CPF é obrigatório");
      return false;
    }

    // Check if CPF has the correct format
    const cpfRegex = /^\d{3}\.\d{3}\.\d{3}-\d{2}$/;
    if (!cpfRegex.test(cpf)) {
      setCpfError("Formato de CPF inválido. Use o formato 000.000.000-00");
      return false;
    }

    // CPF is valid
    setCpfError(null);
    return true;
  };

  const formatCPF = (value: string) => {
    // Remove all non-digit characters
    const digits = value.replace(/\D/g, "");

    // Limit to 11 digits (CPF length)
    const cpfDigits = digits.slice(0, 11);

    // Apply the mask
    let formattedCPF = "";

    if (cpfDigits.length > 0) {
      formattedCPF = cpfDigits.slice(0, 3);

      if (cpfDigits.length > 3) {
        formattedCPF += "." + cpfDigits.slice(3, 6);
      }

      if (cpfDigits.length > 6) {
        formattedCPF += "." + cpfDigits.slice(6, 9);
      }

      if (cpfDigits.length > 9) {
        formattedCPF += "-" + cpfDigits.slice(9, 11);
      }
    }

    return formattedCPF;
  };

  const handleCPFChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const formattedValue = formatCPF(value);
    setCpf(formattedValue);

    // Only validate if we have some input
    if (formattedValue) {
      // If we have a complete CPF (11 digits), validate it
      const digits = formattedValue.replace(/\D/g, "");
      if (digits.length === 11) {
        validateCPF(formattedValue);
      } else {
        // If CPF is incomplete, show a different message
        setCpfError("CPF incompleto");
      }
    } else {
      setCpfError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    // Validate email before submission
    const isEmailValid = validateEmail(email);

    // If email is not valid, don't proceed with form submission
    if (!isEmailValid) {
      return;
    }

    const result = await register({
      email: email,
      nome: nome,
      cpf: cpf,
      password: password,
      groups: selectedGroup ? selectedGroup : "",
    });

    if (result.success) {
      refreshUser(); // Atualiza o contexto após registro
      setIsSuccess(true);
    } else {
      setErrorMessage(result.message);
      return;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-pink-400 p-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -right-20 top-20 w-96 h-96 bg-white rounded-full transform rotate-12 opacity-80"></div>
        <div className="absolute right-40 top-80 w-80 h-80 bg-white rounded-full transform -rotate-12 opacity-80"></div>
        <div className="absolute right-10 bottom-20 w-72 h-72 bg-white rounded-full transform rotate-45 opacity-80"></div>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md z-10">
        <div className="mb-6">
          <div
            className="relative"
            style={{ height: "37px", marginBottom: "24px" }}
          >
            <Image
              src="/images/futuras-cientistas-logo-positive.png"
              alt="Futuras Cientistas"
              width={178}
              height={37}
              className="absolute"
              style={{ top: "0", left: "0" }}
            />
          </div>

          <h1 className="text-2xl font-bold text-gray-800">
            Cadastro primeiro acesso
          </h1>
          <p className="text-sm text-gray-600">
            Já tem uma conta?{" "}
            <Link href="/login" className="text-pink-500 hover:underline">
              ENTRE
            </Link>
          </p>
        </div>

        <div>
          {/* Elemento para exibir mensagens de erro */}
          {errorMessage && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}
        </div>

        {isSuccess ? (
            <Alert className="mb-4 bg-green-50 border-green-200 text-green-800">
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              <AlertDescription>
                Usuário cadastrado com sucesso! Você pode fazer login agora.
                <Link
                  href="/login"
                  className="text-pink-500 hover:underline ml-1"
                >
                  ENTRE
                </Link>
              </AlertDescription>
            </Alert>
          ) : (
            <form className="space-y-4" onSubmit={handleSubmit}>
              <div>
                <Label htmlFor="email" className="text-sm font-medium">
                  E-mail<span className="text-pink-500">*</span>
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="exemplo@email.com"
                  className={`mt-1 ${
                    emailError ? "border-red-500 focus-visible:ring-red-500" : ""
                  }`}
                  value={email}
                  onChange={handleEmailChange}
                  onBlur={() => validateEmail(email)}
                  required
                />
                {emailError && (
                  <p className="text-red-500 text-xs mt-1">{emailError}</p>
                )}
              </div>

              <div>
                <Label htmlFor="name" className="text-sm font-medium">
                  Nome completo<span className="text-pink-500">*</span>
                </Label>
                <Input
                  id="name"
                  placeholder="Nome"
                  className="mt-1"
                  required
                  onChange={(e) => setNome(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="cpf" className="text-sm font-medium">
                  CPF<span className="text-pink-500">*</span>
                </Label>
                <Input
                  id="cpf"
                  placeholder="000.000.000-00"
                  className={`mt-1 ${
                    cpfError ? "border-red-500 focus-visible:ring-red-500" : ""
                  }`}
                  value={cpf}
                  onChange={handleCPFChange}
                  onBlur={() => validateCPF(cpf)}
                  required
                />
                {cpfError && (
                  <p className="text-red-500 text-xs mt-1">{cpfError}</p>
                )}
              </div>

              <div>
                <GroupSelect value={selectedGroup} onChange={setSelectedGroup} />
              </div>

              {/* <div>
                <Label htmlFor="role" className="text-sm font-medium">
                  Você é...
                </Label>
                <Select onValueChange={(value) => setSelectedRole(value)}>
                  <SelectTrigger className="w-full mt-1">
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="estudante">Aluno (a)</SelectItem>
                    <SelectItem value="professor">Professor (a)</SelectItem>
                    <SelectItem value="tutor">Tutor (a)</SelectItem>
                    <SelectItem value="admin">Equipe Futuras</SelectItem>
                  </SelectContent>
                </Select>
              </div> */}

              <div>
                <Label htmlFor="password" className="text-sm font-medium">
                  Senha<span className="text-pink-500">*</span>
                </Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="ExemploSenha2000"
                  className="mt-1"
                  value={password}
                  onChange={handlePasswordChange}
                  required
                />
                <div className="h-1 mt-1 flex space-x-1">
                  <div
                    className={`flex-1 ${
                      passwordStrength >= 1 ? "bg-red-500" : "bg-gray-200"
                    }`}
                  ></div>
                  <div
                    className={`flex-1 ${
                      passwordStrength >= 2 ? "bg-orange-500" : "bg-gray-200"
                    }`}
                  ></div>
                  <div
                    className={`flex-1 ${
                      passwordStrength >= 3 ? "bg-yellow-500" : "bg-gray-200"
                    }`}
                  ></div>
                  <div
                    className={`flex-1 ${
                      passwordStrength >= 4 ? "bg-green-500" : "bg-gray-200"
                    }`}
                  ></div>
                </div>
              </div>

              <div>
                <Label htmlFor="confirm-password" className="text-sm font-medium">
                  Confirmar senha<span className="text-pink-500">*</span>
                </Label>
                <Input
                  id="confirm-password"
                  type="password"
                  placeholder="ExemploSenha2000"
                  className="mt-1"
                  required
                />
              </div>

              <div className="text-xs text-gray-500">* Campos obrigatórios</div>

              <Button
                type="submit"
                className="w-full bg-pink-400 hover:bg-pink-500 text-white"
              >
                Salvar <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </form>
          )}
      </div>
    </div>
  );
}
