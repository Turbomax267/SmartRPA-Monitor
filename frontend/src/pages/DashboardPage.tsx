import { Activity, AlertTriangle, Bot, ChartColumn, CircleOff, Clock3, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'
import { AppBadge } from '../components/common/AppBadge'
import { SurfaceCard } from '../components/common/SurfaceCard'
import { dashboardSnapshot, executionCatalog } from '../mocks/monitorData'

const cardIcons = [Bot, ShieldCheck, CircleOff, AlertTriangle, Activity, ChartColumn, AlertTriangle, Clock3]
const toneStyles = {
  navy: 'bg-brand-blue text-brand-blue',
  green: 'bg-emerald-500 text-emerald-500',
  slate: 'bg-slate-300 text-slate-500',
  amber: 'bg-amber-400 text-amber-500',
  blue: 'bg-blue-500 text-blue-500',
  red: 'bg-red-500 text-red-500',
}

export function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-brand-blue">Dashboard</h1>
        <p className="mt-2 text-lg text-slate-400">Resumen General</p>
        <p className="text-sm text-slate-400">Estado actual de todos los procesos RPA registrados</p>
      </div>

      <div className="grid gap-4 xl:grid-cols-4">
        {dashboardSnapshot.cards.map((card, index) => {
          const Icon = cardIcons[index]
          const tone = toneStyles[card.tone]

          return (
            <SurfaceCard key={card.title} hoverable className="p-5">
              <div className={`mb-4 h-1 w-full rounded-full ${tone.split(' ')[0]}`} />
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-5xl font-bold text-brand-blue">{card.value}</p>
                  <h3 className="mt-3 text-base font-semibold text-brand-blue">{card.title}</h3>
                  <p className="mt-1 text-xs text-slate-400">{card.subtitle}</p>
                </div>
                <div className="rounded-3xl bg-slate-100 p-4 text-slate-300">
                  <Icon size={26} className={tone.split(' ')[1]} />
                </div>
              </div>
            </SurfaceCard>
          )
        })}
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.55fr_0.85fr]">
        <SurfaceCard>
          <div className="flex items-end justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-brand-blue">Ejecuciones por dia</h2>
              <p className="text-sm text-slate-400">Ultimos 14 dias</p>
            </div>
            <AppBadge tone="blue">Actividad estable</AppBadge>
          </div>

          <div className="mt-8 flex h-56 items-end gap-3">
            {dashboardSnapshot.executionsByDay.map((value, index) => (
              <div key={`${value}-${index}`} className="flex flex-1 flex-col items-center gap-3">
                <div
                  className={`w-full rounded-t-2xl ${
                    index === 11 ? 'bg-brand-blue shadow-[0_18px_30px_rgba(4,35,84,0.22)]' : 'bg-slate-500/80'
                  }`}
                  style={{ height: `${Math.max(36, value * 1.5)}px` }}
                />
                <span className="text-[11px] text-slate-300">{index + 1}</span>
              </div>
            ))}
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Errores por Tipo</h2>
          <div className="mt-8 flex justify-center">
            <div className="grid h-44 w-44 place-items-center rounded-full bg-[conic-gradient(#ef4444_0_35%,#f59e0b_35%_63%,#3b82f6_63%_83%,rgba(226,232,240,0.8)_83%_100%)]">
              <div className="grid h-28 w-28 place-items-center rounded-full bg-white text-center">
                <div>
                  <p className="text-4xl font-bold text-brand-blue">72</p>
                  <p className="text-xs text-slate-400">errores</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            {dashboardSnapshot.errorsByType.map((item) => (
              <div key={item.label} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2 text-slate-500">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${
                      item.tone === 'red'
                        ? 'bg-red-500'
                        : item.tone === 'amber'
                          ? 'bg-amber-500'
                          : 'bg-blue-500'
                    }`}
                  />
                  {item.label}
                </div>
                <span
                  className={`font-semibold ${
                    item.tone === 'red' ? 'text-red-500' : item.tone === 'amber' ? 'text-amber-500' : 'text-blue-500'
                  }`}
                >
                  {item.percent}%
                </span>
              </div>
            ))}
          </div>
        </SurfaceCard>
      </div>

      <SurfaceCard className="overflow-hidden p-0">
        <div className="border-b border-slate-100 px-6 py-5">
          <h2 className="text-2xl font-semibold text-brand-blue">Ultimas Ejecuciones</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left">
            <thead className="bg-brand-blue text-sm text-white">
              <tr>
                <th className="px-6 py-4">RPA</th>
                <th className="px-6 py-4">Proceso</th>
                <th className="px-6 py-4">Estado</th>
                <th className="px-6 py-4">Duracion</th>
                <th className="px-6 py-4">Responsable</th>
                <th className="px-6 py-4">Hora</th>
              </tr>
            </thead>
            <tbody>
              {executionCatalog.slice(0, 6).map((execution) => (
                <tr key={execution.id} className="border-b border-slate-100 text-sm text-slate-500 transition hover:bg-slate-50/80">
                  <td className="px-6 py-4 font-semibold text-brand-blue">
                    <Link to={`/executions/${execution.id}`}>{execution.rpaName}</Link>
                  </td>
                  <td className="px-6 py-4">{execution.process}</td>
                  <td className="px-6 py-4">
                    <AppBadge
                      tone={
                        execution.status === 'SUCCESS'
                          ? 'green'
                          : execution.status === 'FAILED'
                            ? 'red'
                            : 'amber'
                      }
                    >
                      {execution.status === 'SUCCESS'
                        ? 'Exitoso'
                        : execution.status === 'FAILED'
                          ? 'Fallido'
                          : 'En revision'}
                    </AppBadge>
                  </td>
                  <td className="px-6 py-4">{execution.durationLabel}</td>
                  <td className="px-6 py-4">{execution.responsible}</td>
                  <td className="px-6 py-4">{execution.timeLabel}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SurfaceCard>
    </div>
  )
}
