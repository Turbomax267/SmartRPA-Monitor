const STORAGE_KEY = 'smartrpa_auth'

export interface StoredSession {
  token: string
  remember: boolean
}

export function saveSession(session: StoredSession) {
  const value = JSON.stringify(session)

  if (session.remember) {
    localStorage.setItem(STORAGE_KEY, value)
    sessionStorage.removeItem(STORAGE_KEY)
    return
  }

  sessionStorage.setItem(STORAGE_KEY, value)
  localStorage.removeItem(STORAGE_KEY)
}

export function getStoredSession(): StoredSession | null {
  const raw = localStorage.getItem(STORAGE_KEY) ?? sessionStorage.getItem(STORAGE_KEY)

  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw) as StoredSession
  } catch {
    clearSession()
    return null
  }
}

export function getStoredToken() {
  return getStoredSession()?.token ?? null
}

export function clearSession() {
  localStorage.removeItem(STORAGE_KEY)
  sessionStorage.removeItem(STORAGE_KEY)
}
