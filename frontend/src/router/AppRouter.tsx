import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { PrivateLayout } from '../components/layout/PrivateLayout'
import { ProtectedRoute } from './ProtectedRoute'
import { PublicRoute } from './PublicRoute'
import { AiAnalysisPage } from '../pages/AiAnalysisPage'
import { DashboardPage } from '../pages/DashboardPage'
import { ExecutionsPage } from '../pages/ExecutionsPage'
import { IncidentsPage } from '../pages/IncidentsPage'
import { LoginPage } from '../pages/LoginPage'
import { MetricsPage } from '../pages/MetricsPage'
import { RpasPage } from '../pages/RpasPage'
import { SettingsPage } from '../pages/SettingsPage'
import { UsersPage } from '../pages/UsersPage'

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<PublicRoute />}>
          <Route path="/login" element={<LoginPage />} />
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<PrivateLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/rpas" element={<RpasPage />} />
            <Route path="/executions" element={<ExecutionsPage />} />
            <Route path="/incidents" element={<IncidentsPage />} />
            <Route path="/ai-analysis" element={<AiAnalysisPage />} />
            <Route path="/metrics" element={<MetricsPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
