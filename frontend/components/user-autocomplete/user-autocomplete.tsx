"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { useUsers } from "@/hooks/use-users"
import type { User } from "@/types/user"
import styles from "./userautocomplete.module.css"

interface UserAutocompleteProps {
  value: string
  onChange: (user: User) => void
  className?: string
  placeholder?: string
  hasError?: boolean,
  groupName: string
}

export default function UserAutocomplete({
  value,
  onChange,
  className = "",
  placeholder = "Buscar por nome...",
  hasError = false,
  groupName = "estudante"
}: UserAutocompleteProps) {
  const [inputValue, setInputValue] = useState("")
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLUListElement>(null)

  const { users: defaultUsers, isLoading, error, searchUsers } = useUsers(groupName)
  const [users, setUsers] = useState(defaultUsers)

  // Encontrar o usuário selecionado pelo ID
  const userSelecionado = users.find((user) => user.id === value)

  // Sincronizar o valor do input com o usuário selecionado
  useEffect(() => {
    if (userSelecionado) {
      setInputValue(userSelecionado.name)
    } else if (value === "") {
      setInputValue("")
    }
  }, [userSelecionado, value])

  // Buscar usuários quando o input mudar
  useEffect(() => {
    const timer = setTimeout(() => {
      if (inputValue.trim()) {
        setUsers(searchUsers(inputValue.trim()))
      } else {
        handleFocus()
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [inputValue, searchUsers])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setInputValue(newValue)
    setIsOpen(true)
    setSelectedIndex(-1)

    // Se o input estiver vazio, limpar a seleção
    if (!newValue.trim()) {
      onChange(null)
    }
  }

  const handleUserSelect = (user: User) => {
    setInputValue(user.name)
    setIsOpen(false)
    setSelectedIndex(-1)
    onChange(user)
    inputRef.current?.blur()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || users.length === 0) return

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault()
        setSelectedIndex((prev) => (prev < users.length - 1 ? prev + 1 : 0))
        break
      case "ArrowUp":
        e.preventDefault()
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : users.length - 1))
        break
      case "Enter":
        e.preventDefault()
        if (selectedIndex >= 0 && selectedIndex < users.length) {
          handleUserSelect(users[selectedIndex])
        }
        break
      case "Escape":
        setIsOpen(false)
        setSelectedIndex(-1)
        inputRef.current?.blur()
        break
    }
  }

  const handleFocus = () => {
    if (inputValue.trim()) {
      setIsOpen(true)
    } else {
      setIsOpen(false)
    }
  }

  const handleBlur = (e: React.FocusEvent) => {
    // Delay para permitir clique nas opções
    setTimeout(() => {
      if (e.currentTarget && !e.currentTarget.contains(document.activeElement)) {
        setIsOpen(false)
        setSelectedIndex(-1)
      }
    }, 150)
  }

  // Scroll para o item selecionado
  useEffect(() => {
    if (selectedIndex >= 0 && listRef.current) {
      const selectedElement = listRef.current.children[selectedIndex] as HTMLElement
      if (selectedElement) {
        selectedElement.scrollIntoView({
          block: "nearest",
          behavior: "smooth",
        })
      }
    }
  }, [selectedIndex])

  return (
    <div className={styles.container} onBlur={handleBlur}>
      <input
        ref={inputRef}
        type="text"
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={handleFocus}
        placeholder={placeholder}
        className={`${styles.input} ${hasError ? styles.inputError : ""} ${className}`}
        autoComplete="off"
      />

      {isOpen && (
        <div className={styles.dropdown}>
          {isLoading && <div className={styles.loadingMessage}>Buscando usuários...</div>}

          {error && <div className={styles.errorMessage}>{error}</div>}

          {!isLoading && !error && users.length === 0 && inputValue.trim() && (
            <div className={styles.noResults}>Nenhum usuário encontrado para "{inputValue}"</div>
          )}

          {!isLoading && !error && users.length > 0 && (
            <ul ref={listRef} className={styles.list}>
              {users.map((user, index) => (
                <li
                  key={user.id}
                  className={`${styles.listItem} ${
                    index === selectedIndex ? styles.listItemSelected : ""
                  } ${user.id === value ? styles.listItemActive : ""}`}
                  onClick={() => handleUserSelect(user)}
                >
                  <div className={styles.userName}>{user.name}</div>
                  <div className={styles.userEmail}>{user.email}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
