import { createContext, useEffect, useMemo, useState } from 'react'
import { loginRequest, logoutRequest, meRequest } from '../api/auth.api'
import type { LoginFormValues, User } from '../interfaces'
import { clearSession, getStoredSession, saveSession } from '../utils/storage'

interface LoginOptions {
  remember: boolean
}

interface AuthContextValue {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (values: LoginFormValues, options: LoginOptions) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const storedSession = getStoredSession()
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(storedSession?.token ?? null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshUser = async () => {
    const response = await meRequest()
    setUser(response.data)
  }

  const logout = async () => {
    try {
      if (token) {
        await logoutRequest()
      }
    } finally {
      clearSession()
      setToken(null)
      setUser(null)
    }
  }

  const login = async (values: LoginFormValues, options: LoginOptions) => {
    const response = await loginRequest(values)

    saveSession({
      token: response.data.token,
      remember: options.remember,
    })

    setToken(response.data.token)
    setUser(response.data.user)
  }

  useEffect(() => {
    const bootstrap = async () => {
      const session = getStoredSession()

      if (!session?.token) {
        setIsLoading(false)
        return
      }

      try {
        setToken(session.token)
        await refreshUser()
      } catch {
        clearSession()
        setToken(null)
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    void bootstrap()
  }, [])

  useEffect(() => {
    const handleUnauthorized = () => {
      void logout()
    }

    window.addEventListener('auth:unauthorized', handleUnauthorized)

    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized)
  }, [token])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token && user),
      isLoading,
      login,
      logout,
      refreshUser,
    }),
    [user, token, isLoading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
