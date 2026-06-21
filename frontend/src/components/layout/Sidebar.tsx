import {
  Bot,
  BrainCircuit,
  ChartColumn,
  ChevronRight,
  LayoutDashboard,
  LogOut,
  Settings,
  ShieldAlert,
  Users,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'
import logo from '../../assets/branding/logo.png'
import { useAuth } from '../../hooks/useAuth'

const navigationItems = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { label: 'RPA / Bots', path: '/rpas', icon: Bot },
  { label: 'Ejecuciones', path: '/executions', icon: ChevronRight },
  { label: 'Alertas e Incidentes', path: '/incidents', icon: ShieldAlert },
  { label: 'Análisis IA', path: '/ai-analysis', icon: BrainCircuit },
  { label: 'Métricas', path: '/metrics', icon: ChartColumn },
  { label: 'Usuarios y Roles', path: '/users', icon: Users },
  { label: 'Configuración', path: '/settings', icon: Settings },
]

export function Sidebar() {
  const { logout, user } = useAuth()

  return (
    <aside className="flex h-screen w-full max-w-72 flex-col bg-brand-blue px-5 py-6 text-white">
      <div className="flex items-center justify-center border-b border-white/10 pb-6">
        <img src={logo} alt="SmartRPA Monitor" className="h-20 w-auto object-contain" />
      </div>

      <div className="mt-8">
        <p className="px-3 text-[10px] font-semibold uppercase tracking-[0.35em] text-white/35">
          Menú principal
        </p>

        <nav className="mt-4 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition ${
                    isActive
                      ? 'bg-brand-yellow text-brand-blue shadow-lg'
                      : 'text-white/80 hover:bg-white/8 hover:text-white'
                  }`
                }
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </nav>
      </div>

      <button
        type="button"
        onClick={() => void logout()}
        className="mt-auto flex items-center gap-3 rounded-2xl border border-white/10 px-4 py-3 text-sm font-medium text-white/85 transition hover:bg-white/8"
      >
        <LogOut size={18} />
        <span>Cerrar sesión</span>
      </button>

      <div className="mt-6 flex items-center gap-3 border-t border-white/10 pt-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-yellow font-bold text-brand-blue">
          {user?.name?.slice(0, 2).toUpperCase() ?? 'AD'}
        </div>
        <div>
          <p className="text-sm font-semibold">{user?.name ?? 'Usuario'}</p>
          <p className="text-xs text-white/55">{user?.role?.display_name ?? 'Rol no definido'}</p>
        </div>
      </div>
    </aside>
  )
}
