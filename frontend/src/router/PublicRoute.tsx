import { Navigate, Outlet } from 'react-router-dom'
import { LoaderScreen } from '../components/common/LoaderScreen'
import { useAuth } from '../hooks/useAuth'

export function PublicRoute() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <LoaderScreen message="Validando acceso..." />
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
