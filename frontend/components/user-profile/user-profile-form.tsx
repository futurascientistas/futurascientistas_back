"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Card } from "@/components/ui/card"
import { Upload } from "lucide-react"

export function UserProfileForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // Simulate form submission
    setTimeout(() => {
      setIsSubmitting(false)
      // Show success message or redirect
    }, 1500)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Dados Pessoais */}
      <Card className="p-6">
        <Accordion type="single" collapsible defaultValue="dados-pessoais">
          <AccordionItem value="dados-pessoais" className="border-none">
            <AccordionTrigger className="py-2 text-lg font-medium">Dados Pessoais</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pt-4">
                <div>
                  <Label htmlFor="nome-completo">Nome Completo</Label>
                  <Input id="nome-completo" className="mt-1" />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="cpf">CPF</Label>
                    <Input id="cpf" className="mt-1" />
                  </div>
                  <div>
                    <Label htmlFor="data-nascimento">Data de nascimento</Label>
                    <Input id="data-nascimento" className="mt-1" placeholder="DD/MM/AAAA" />
                  </div>
                </div>

                <div>
                  <Label htmlFor="rg">RG</Label>
                  <Input id="rg" className="mt-1" />
                </div>

                <div>
                  <Label htmlFor="telefone">Telefone</Label>
                  <Input id="telefone" className="mt-1" />
                </div>

                <div>
                  <Label htmlFor="pronomes">Pronomes</Label>
                  <Input id="pronomes" className="mt-1" />
                </div>

                <div>
                  <Label htmlFor="lattes">Lattes</Label>
                  <Input id="lattes" className="mt-1" />
                </div>

                <div>
                  <Label htmlFor="upload-cpf">Upload CPF</Label>
                  <div className="flex mt-1">
                    <Input id="upload-cpf" className="rounded-r-none" readOnly />
                    <Button type="button" variant="secondary" className="rounded-l-none border border-l-0 border-input">
                      <Upload className="h-4 w-4 mr-2" />
                      Selecionar arquivo
                    </Button>
                  </div>
                </div>

                <div>
                  <Label htmlFor="upload-rg">Upload RG (Frente e verso)</Label>
                  <div className="flex mt-1">
                    <Input id="upload-rg" className="rounded-r-none" readOnly />
                    <Button type="button" variant="secondary" className="rounded-l-none border border-l-0 border-input">
                      <Upload className="h-4 w-4 mr-2" />
                      Selecionar arquivo
                    </Button>
                  </div>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </Card>

      {/* Localização e Endereço */}
      <Card className="p-6">
        <Accordion type="single" collapsible defaultValue="localizacao-endereco">
          <AccordionItem value="localizacao-endereco" className="border-none">
            <AccordionTrigger className="py-2 text-lg font-medium">Localização e Endereço</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pt-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <Label htmlFor="cep">CEP</Label>
                    <Input id="cep" className="mt-1" />
                  </div>
                  <div className="md:col-span-3">
                    <Label htmlFor="rua">Rua</Label>
                    <Input id="rua" className="mt-1" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <div className="md:col-span-2">
                    <Label htmlFor="bairro">Bairro</Label>
                    <Input id="bairro" className="mt-1" />
                  </div>
                  <div>
                    <Label htmlFor="numero">Número</Label>
                    <Input id="numero" className="mt-1" />
                  </div>
                  <div className="md:col-span-2">
                    <Label htmlFor="complemento">Complemento</Label>
                    <Input id="complemento" className="mt-1" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="cidade">Cidade</Label>
                    <Input id="cidade" className="mt-1" />
                  </div>
                  <div>
                    <Label htmlFor="estado">Estado/UF</Label>
                    <Input id="estado" className="mt-1" />
                  </div>
                </div>

                <div>
                  <Label htmlFor="upload-comprovante">Upload comprovante de residência</Label>
                  <div className="flex mt-1">
                    <Input id="upload-comprovante" className="rounded-r-none" readOnly />
                    <Button type="button" variant="secondary" className="rounded-l-none border border-l-0 border-input">
                      <Upload className="h-4 w-4 mr-2" />
                      Selecionar arquivo
                    </Button>
                  </div>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </Card>

      {/* Classificação Social */}
      <Card className="p-6">
        <Accordion type="single" collapsible defaultValue="classificacao-social">
          <AccordionItem value="classificacao-social" className="border-none">
            <AccordionTrigger className="py-2 text-lg font-medium">Classificação Social</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pt-4">
                <div>
                  <Label htmlFor="genero">Gênero</Label>
                  <Select>
                    <SelectTrigger id="genero" className="mt-1">
                      <SelectValue placeholder="Outra identidade de Gênero" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="feminino">Feminino</SelectItem>
                      <SelectItem value="masculino">Masculino</SelectItem>
                      <SelectItem value="nao-binario">Não-binário</SelectItem>
                      <SelectItem value="outro">Outra identidade de Gênero</SelectItem>
                      <SelectItem value="prefiro-nao-dizer">Prefiro não dizer</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="raca">Autodeclaração racial</Label>
                  <Select>
                    <SelectTrigger id="raca" className="mt-1">
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="branca">Branca</SelectItem>
                      <SelectItem value="preta">Preta</SelectItem>
                      <SelectItem value="parda">Parda</SelectItem>
                      <SelectItem value="amarela">Amarela</SelectItem>
                      <SelectItem value="indigena">Indígena</SelectItem>
                      <SelectItem value="prefiro-nao-dizer">Prefiro não dizer</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="deficiencias">Deficiências</Label>
                  <Select>
                    <SelectTrigger id="deficiencias" className="mt-1">
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="nenhuma">Nenhuma</SelectItem>
                      <SelectItem value="fisica">Física</SelectItem>
                      <SelectItem value="auditiva">Auditiva</SelectItem>
                      <SelectItem value="visual">Visual</SelectItem>
                      <SelectItem value="intelectual">Intelectual</SelectItem>
                      <SelectItem value="multipla">Múltipla</SelectItem>
                      <SelectItem value="prefiro-nao-dizer">Prefiro não dizer</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </Card>

      {/* Dados da Escola */}
      <Card className="p-6">
        <Accordion type="single" collapsible defaultValue="dados-escola">
          <AccordionItem value="dados-escola" className="border-none">
            <AccordionTrigger className="py-2 text-lg font-medium">Dados da Escola</AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pt-4">
                <div>
                  <Label htmlFor="nome-escola">Nome da escola</Label>
                  <Input id="nome-escola" className="mt-1" />
                </div>

                <div>
                  <Label htmlFor="tipo-ensino">Tipo de ensino</Label>
                  <Select>
                    <SelectTrigger id="tipo-ensino" className="mt-1">
                      <SelectValue placeholder="Regular" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="regular">Regular</SelectItem>
                      <SelectItem value="tecnico">Técnico</SelectItem>
                      <SelectItem value="eja">EJA</SelectItem>
                      <SelectItem value="integral">Integral</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <Label htmlFor="cep-escola">CEP</Label>
                    <Input id="cep-escola" className="mt-1" />
                  </div>
                  <div className="md:col-span-3">
                    <Label htmlFor="rua-escola">Rua</Label>
                    <Input id="rua-escola" className="mt-1" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <div className="md:col-span-2">
                    <Label htmlFor="bairro-escola">Bairro</Label>
                    <Input id="bairro-escola" className="mt-1" />
                  </div>
                  <div>
                    <Label htmlFor="numero-escola">Número</Label>
                    <Input id="numero-escola" className="mt-1" />
                  </div>
                  <div className="md:col-span-2">
                    <Label htmlFor="complemento-escola">Complemento</Label>
                    <Input id="complemento-escola" className="mt-1" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="cidade-escola">Cidade</Label>
                    <Input id="cidade-escola" className="mt-1" />
                  </div>
                  <div>
                    <Label htmlFor="estado-escola">Estado/UF</Label>
                    <Select>
                      <SelectTrigger id="estado-escola" className="mt-1">
                        <SelectValue placeholder="Selecione" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="AC">AC</SelectItem>
                        <SelectItem value="AL">AL</SelectItem>
                        <SelectItem value="AP">AP</SelectItem>
                        <SelectItem value="AM">AM</SelectItem>
                        <SelectItem value="BA">BA</SelectItem>
                        <SelectItem value="CE">CE</SelectItem>
                        <SelectItem value="DF">DF</SelectItem>
                        <SelectItem value="ES">ES</SelectItem>
                        <SelectItem value="GO">GO</SelectItem>
                        <SelectItem value="MA">MA</SelectItem>
                        <SelectItem value="MT">MT</SelectItem>
                        <SelectItem value="MS">MS</SelectItem>
                        <SelectItem value="MG">MG</SelectItem>
                        <SelectItem value="PA">PA</SelectItem>
                        <SelectItem value="PB">PB</SelectItem>
                        <SelectItem value="PR">PR</SelectItem>
                        <SelectItem value="PE">PE</SelectItem>
                        <SelectItem value="PI">PI</SelectItem>
                        <SelectItem value="RJ">RJ</SelectItem>
                        <SelectItem value="RN">RN</SelectItem>
                        <SelectItem value="RS">RS</SelectItem>
                        <SelectItem value="RO">RO</SelectItem>
                        <SelectItem value="RR">RR</SelectItem>
                        <SelectItem value="SC">SC</SelectItem>
                        <SelectItem value="SP">SP</SelectItem>
                        <SelectItem value="SE">SE</SelectItem>
                        <SelectItem value="TO">TO</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="telefone-escola">Telefone da escola</Label>
                  <Input id="telefone-escola" className="mt-1" />
                </div>

                <div>
                  <Label htmlFor="telefone-responsavel">Telefone de um responsável pela escola</Label>
                  <Input id="telefone-responsavel" className="mt-1" />
                </div>

                <div>
                  <Label htmlFor="nome-responsavel">Nome do contato responsável pela escola</Label>
                  <Input id="nome-responsavel" className="mt-1" />
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </Card>

      <div className="flex justify-end">
        <Button type="submit" className="bg-pink-400 hover:bg-pink-500 text-white" disabled={isSubmitting}>
          {isSubmitting ? "Salvando..." : "Salvar alterações"}
        </Button>
      </div>
    </form>
  )
}
