import {
  Activity,
  Bot,
  BrainCircuit,
  ChevronDown,
  ChartColumn,
  FileText,
  LayoutDashboard,
  LogOut,
  Settings,
  ShieldAlert,
  Users,
} from 'lucide-react'
import { NavLink, useLocation } from 'react-router-dom'
import logo from '../../assets/branding/logo.png'
import { useAuth } from '../../hooks/useAuth'

const navigationItems = [
  { label: 'Dashboard', path: '/dashboard', match: '/dashboard', icon: LayoutDashboard },
  { label: 'RPA / Bots', path: '/rpas', match: '/rpas', icon: Bot },
  { label: 'Ejecuciones', path: '/executions', match: '/executions', icon: Activity, exact: true },
  { label: 'Logs', path: '/executions', match: '/executions/', icon: FileText },
  { label: 'Alertas', path: '/incidents', match: '/incidents', icon: ShieldAlert },
  { label: 'Analisis IA', path: '/ai-analysis', match: '/ai-analysis', icon: BrainCircuit },
  { label: 'Metricas', path: '/metrics', match: '/metrics', icon: ChartColumn },
  { label: 'Usuarios y Roles', path: '/users', match: '/users', icon: Users },
  { label: 'Configuracion', path: '/settings', match: '/settings', icon: Settings },
]

export function Sidebar() {
  const location = useLocation()
  const { logout, user } = useAuth()

  return (
    <aside className="sticky top-0 flex h-screen w-full max-w-[300px] flex-col overflow-hidden bg-brand-blue text-white">
      <div className="border-b border-white/10 px-5 py-5">
        <img src={logo} alt="SmartRPA Monitor" className="h-40 w-full object-contain object-left" />
      </div>

      <div className="mt-6 px-3">
        <p className="px-4 text-[11px] font-semibold uppercase tracking-[0.35em] text-white/35">
          Menu principal
        </p>

        <nav className="mt-4 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon
            const selected = item.exact
              ? location.pathname === item.match
              : location.pathname === item.match || location.pathname.startsWith(item.match)

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`group flex items-center gap-3 rounded-2xl px-4 py-3.5 text-base font-medium transition duration-300 ${
                  selected
                    ? 'bg-brand-yellow text-brand-blue shadow-[0_18px_34px_rgba(250,214,52,0.25)]'
                    : 'text-white/78 hover:bg-white/8 hover:text-white'
                }`}
              >
                <Icon size={18} className="transition group-hover:scale-105" />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </nav>
      </div>

      <button
        type="button"
        onClick={() => void logout()}
        className="mx-3 mt-auto flex items-center gap-3 rounded-2xl border border-white/10 px-4 py-3 text-sm font-medium text-white/85 transition hover:bg-white/8"
      >
        <LogOut size={18} />
        <span>Cerrar sesion</span>
      </button>

      <div className="mx-3 mt-4 flex items-center gap-3 border-t border-white/10 px-1 pb-5 pt-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-yellow font-bold text-brand-blue">
          {user?.name?.slice(0, 2).toUpperCase() ?? 'AD'}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold">{user?.name ?? 'Usuario'}</p>
          <p className="text-xs text-white/55">{user?.role?.display_name ?? 'Administrador'}</p>
        </div>
        <button type="button" className="rounded-full p-2 text-white/50 transition hover:bg-white/10 hover:text-white">
          <ChevronDown size={16} />
        </button>
      </div>
    </aside>
  )
}
