import { Bell } from 'lucide-react'
import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { useAuth } from '../../hooks/useAuth'

export function PrivateLayout() {
  const location = useLocation()
  const { user } = useAuth()

  return (
    <div className="flex min-h-screen bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.97),_rgba(241,245,249,0.98)_45%,_rgba(230,236,247,1)_100%)]">
      <Sidebar />

      <div className="flex min-h-screen flex-1 flex-col overflow-hidden">
        <header className="sticky top-0 z-20 flex items-center justify-end border-b border-white/60 bg-white/82 px-8 py-5 shadow-[0_10px_30px_rgba(15,23,42,0.05)] backdrop-blur-xl">
          <div className="flex items-center gap-4">
            <p className="hidden text-sm text-slate-400 md:block">Actualizado: hoy, 09:45 AM</p>
            <button
              type="button"
              className="relative rounded-2xl border border-slate-100 bg-white p-3 text-slate-500 transition hover:-translate-y-0.5 hover:shadow-lg"
            >
              <Bell size={18} />
              <span className="absolute right-2 top-1 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-red-100 px-1 text-[10px] font-bold text-red-500">
                3
              </span>
            </button>
            <div className="rounded-full bg-brand-blue px-5 py-2.5 text-sm font-semibold text-white shadow-[0_12px_24px_rgba(4,35,84,0.18)]">
              {user?.role?.display_name ?? 'Admin'}
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div key={location.pathname} className="animate-soft-reveal">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
