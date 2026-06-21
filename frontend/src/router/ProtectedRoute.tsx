import { Navigate, Outlet } from 'react-router-dom'
import { LoaderScreen } from '../components/common/LoaderScreen'
import { useAuth } from '../hooks/useAuth'

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <LoaderScreen message="Restaurando sesión..." />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
