"use client";

import { Check, X } from "lucide-react";
import styles from "./successmodal.module.css";

interface SuccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  message?: string;
  description?: string;
  buttonText?: string;
}

export default function SuccessModal({
  isOpen,
  onClose,
  title = "Sucesso!",
  message = "Cadastro realizado com sucesso.",
  description = "",
  buttonText = "OK",
}: SuccessModalProps) {
  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose}>
          <X size={20} />
        </button>

        <div className={styles.content}>
          <div className={styles.iconContainer}>
            <Check className={styles.checkIcon} />
          </div>

          <h2 className={styles.title}>{title}</h2>

          <p className={styles.message}>{message}</p>

          <p className={styles.description}>{description}</p>

          <button className={styles.okButton} onClick={onClose}>
            {buttonText}
          </button>
        </div>
      </div>
    </div>
  );
}
