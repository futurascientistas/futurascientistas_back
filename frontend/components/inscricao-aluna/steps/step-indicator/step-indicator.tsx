import styles from "./stepindicator.module.css"

interface StepIndicatorProps {
  currentStep: number
  totalSteps: number
}

export function StepIndicator({ currentStep, totalSteps }: StepIndicatorProps) {
  return (
    <div className={styles.container}>
      <div className={styles.stepInfo}>
        <span className={styles.stepText}>
          Etapa {currentStep} de {totalSteps}
        </span>
      </div>
      <div className={styles.progressBar}>
        <div className={styles.progressFill} style={{ width: `${(currentStep / totalSteps) * 100}%` }}></div>
      </div>
    </div>
  )
}
