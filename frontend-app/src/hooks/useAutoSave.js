import { useState, useEffect, useCallback } from 'react'

const STORAGE_KEY = 'asset-organizer-draft'

/**
 * Hook tự động lưu form vào localStorage khi user gõ.
 * Khi F5, dữ liệu được khôi phục từ localStorage.
 */
export function useAutoSave() {
  const [projectName, setProjectName] = useState(() => {
    return localStorage.getItem(`${STORAGE_KEY}-name`) || ''
  })

  const [rawText, setRawText] = useState(() => {
    return localStorage.getItem(`${STORAGE_KEY}-text`) || ''
  })

  // Auto-save: mỗi lần projectName thay đổi → lưu
  useEffect(() => {
    localStorage.setItem(`${STORAGE_KEY}-name`, projectName)
  }, [projectName])

  // Auto-save: mỗi lần rawText thay đổi → lưu
  useEffect(() => {
    localStorage.setItem(`${STORAGE_KEY}-text`, rawText)
  }, [rawText])

  // Clear toàn bộ draft
  const clear = useCallback(() => {
    setProjectName('')
    setRawText('')
    localStorage.removeItem(`${STORAGE_KEY}-name`)
    localStorage.removeItem(`${STORAGE_KEY}-text`)
  }, [])

  return { projectName, setProjectName, rawText, setRawText, clear }
}
