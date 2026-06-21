import { Bell } from 'lucide-react'
import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { useAuth } from '../../hooks/useAuth'

const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/rpas': 'RPA / Bots',
  '/executions': 'Ejecuciones',
  '/incidents': 'Alertas e Incidentes',
  '/ai-analysis': 'Análisis IA',
  '/metrics': 'Métricas',
  '/users': 'Usuarios y Roles',
  '/settings': 'Configuración',
}

export function PrivateLayout() {
  const location = useLocation()
  const { user } = useAuth()
  const pageTitle = pageTitles[location.pathname] ?? 'SmartRPA Monitor'

  return (
    <div className="flex min-h-screen bg-slate-100">
      <Sidebar />

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-8 py-5 shadow-sm">
          <div>
            <h2 className="text-3xl font-bold text-brand-blue">{pageTitle}</h2>
          </div>

          <div className="flex items-center gap-4">
            <p className="hidden text-sm text-slate-400 md:block">Actualizado: hoy 09:45 AM</p>
            <button
              type="button"
              className="relative rounded-2xl bg-slate-100 p-3 text-slate-500 transition hover:bg-slate-200"
            >
              <Bell size={18} />
              <span className="absolute right-2 top-1 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-red-100 px-1 text-[10px] font-bold text-red-500">
                3
              </span>
            </button>
            <div className="rounded-full bg-brand-blue px-4 py-2 text-sm font-semibold text-white">
              {user?.role?.display_name ?? 'Admin'}
            </div>
          </div>
        </header>

        <main className="flex-1 p-6 md:p-8">
          <div key={location.pathname} className="animate-soft-reveal">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
