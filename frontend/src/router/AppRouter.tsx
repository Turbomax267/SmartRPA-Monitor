import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { PrivateLayout } from '../components/layout/PrivateLayout'
import { ProtectedRoute } from './ProtectedRoute'
import { PublicRoute } from './PublicRoute'
import { AiAnalysisPage } from '../pages/AiAnalysisPage'
import { DashboardPage } from '../pages/DashboardPage'
import { ExecutionDetailPage } from '../pages/ExecutionDetailPage'
import { ExecutionsPage } from '../pages/ExecutionsPage'
import { IncidentDetailPage } from '../pages/IncidentDetailPage'
import { IncidentsPage } from '../pages/IncidentsPage'
import { LoginPage } from '../pages/LoginPage'
import { MetricsPage } from '../pages/MetricsPage'
import { RpaDetailPage } from '../pages/RpaDetailPage'
import { RpasPage } from '../pages/RpasPage'
import { SettingsPage } from '../pages/SettingsPage'
import { UserFormPage } from '../pages/UserFormPage'
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
            <Route path="/rpas/:rpaId" element={<RpaDetailPage />} />
            <Route path="/executions" element={<ExecutionsPage />} />
            <Route path="/executions/:executionId" element={<ExecutionDetailPage />} />
            <Route path="/incidents" element={<IncidentsPage />} />
            <Route path="/incidents/:incidentId" element={<IncidentDetailPage />} />
            <Route path="/ai-analysis" element={<AiAnalysisPage />} />
            <Route path="/ai-analysis/:analysisId" element={<AiAnalysisPage />} />
            <Route path="/metrics" element={<MetricsPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/users/new" element={<UserFormPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
