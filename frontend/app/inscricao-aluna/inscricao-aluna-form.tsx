"use client"

import { useState } from "react"

import { StepIndicator } from "@/components/inscricao-aluna/steps/step-indicator/step-indicator"
import { Step1 } from "@/components/inscricao-aluna/steps/step1/step1"
import { Step2 } from "@/components/inscricao-aluna/steps/step2/step2"
import { Step3 } from "@/components/inscricao-aluna/steps/step3/step3"
import { Step4 } from "@/components/inscricao-aluna/steps/step4/step4"
import { Step5 } from "@/components/inscricao-aluna/steps/step5/step5"
import { Step6 } from "@/components/inscricao-aluna/steps/step6/step6"
import { ProjectSelection } from "@/components/project-selection/project-selection"
import styles from "./inscricaoaluna.module.css"

export default function InscricaoPage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({})

  console.log("Current step:", currentStep)
  console.log("Form data:", formData)

  const handleStepComplete = async (stepData: any) => {
    console.log(`Tentando salvar etapa ${currentStep} com dados:`, stepData)

    try {
      // Validate required fields before proceeding
      if (!stepData || Object.keys(stepData).length === 0) {
        throw new Error("Dados do formulário estão vazios")
      }

      // For development/testing, we'll simulate API success
      // Uncomment and modify this when your API is ready
      /*
      const response = await fetch("http://localhost:8000/inscricoes/inscrever_se/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          step: currentStep,
          data: stepData,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || "Erro ao salvar dados")
      }
      */

      // Simulate successful API response
      console.log(`Dados da etapa ${currentStep} salvos com sucesso`)

      // Update form data
      setFormData((prev) => {
        const newData = { ...prev, [`step${currentStep}`]: stepData }
        console.log("Form data atualizado:", newData)
        return newData
      })

      // Navigate to next step
      if (currentStep < 6) {
        console.log(`Navegando para etapa ${currentStep + 1}`)
        setCurrentStep(currentStep + 1)
      } else {
        console.log("Navegando para seleção de projetos")
        setCurrentStep(7)
      }
    } catch (error) {
      console.error("Erro ao salvar dados:", error)
      alert(`Erro ao salvar dados: ${error.message}`)
    }
  }

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return <Step1 onComplete={handleStepComplete} />
      case 2:
        return <Step2 onComplete={handleStepComplete} />
      case 3:
        return <Step3 onComplete={handleStepComplete} />
      case 4:
        return <Step4 onComplete={handleStepComplete} />
      case 5:
        return <Step5 onComplete={handleStepComplete} />
      case 6:
        return <Step6 onComplete={handleStepComplete} />
      case 7:
        return <ProjectSelection />
      default:
        return <Step1 onComplete={handleStepComplete} />
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.mainContent}>
       

        <main className={styles.main}>
          <div className={styles.content}>
            {currentStep <= 6 && <StepIndicator currentStep={currentStep} totalSteps={6} />}
            {renderCurrentStep()}
          </div>
        </main>
      </div>
    </div>
  )
}
