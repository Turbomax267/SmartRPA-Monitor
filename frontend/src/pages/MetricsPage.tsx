import { SurfaceCard } from '../components/common/SurfaceCard'
import { dashboardSnapshot, metricsSnapshot } from '../mocks/monitorData'

export function MetricsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-brand-blue">Metricas y Reportes</h1>
        <p className="mt-2 text-lg text-brand-blue">Indicadores de comportamiento y rendimiento del sistema RPA</p>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_1fr_0.9fr_0.86fr_0.86fr]">
        <input className="rounded-2xl border border-white/70 bg-white/92 px-4 py-4 text-sm shadow-soft outline-none" placeholder="Fecha inicio" />
        <input className="rounded-2xl border border-white/70 bg-white/92 px-4 py-4 text-sm shadow-soft outline-none" placeholder="Fecha fin" />
        <select className="rounded-2xl border border-white/70 bg-white/92 px-4 py-4 text-sm shadow-soft outline-none">
          <option>RPA</option>
        </select>
        <button className="rounded-2xl bg-red-500 px-5 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(239,68,68,0.16)] transition hover:-translate-y-0.5">
          Exportar PDF
        </button>
        <button className="rounded-2xl bg-emerald-500 px-5 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(34,197,94,0.18)] transition hover:-translate-y-0.5">
          Exportar Excel
        </button>
      </div>

      <div className="grid gap-4 xl:grid-cols-4">
        {dashboardSnapshot.cards.slice(4).map((card) => (
          <SurfaceCard key={card.title} className="p-5">
            <div className={`mb-4 h-1 w-full rounded-full ${card.tone === 'blue' ? 'bg-blue-500' : card.tone === 'green' ? 'bg-emerald-500' : card.tone === 'red' ? 'bg-red-500' : 'bg-amber-500'}`} />
            <p className={`text-4xl font-bold ${card.tone === 'blue' ? 'text-blue-500' : card.tone === 'green' ? 'text-emerald-500' : card.tone === 'red' ? 'text-red-500' : 'text-amber-500'}`}>
              {card.value}
            </p>
            <p className="mt-2 text-lg font-semibold text-brand-blue">{card.title}</p>
            <p className="text-sm text-slate-400">{card.subtitle}</p>
          </SurfaceCard>
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.6fr_0.8fr]">
        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Ejecuciones por Dia</h2>
          <p className="text-sm text-slate-400">Ultimos 30 dias</p>
          <div className="mt-7 flex h-56 items-end gap-2">
            {metricsSnapshot.dailyExecutions.map((value, index) => (
              <div
                key={`${value}-${index}`}
                className="flex-1 rounded-t-xl bg-slate-500/80"
                style={{ height: `${Math.max(32, value * 1.4)}px` }}
              />
            ))}
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Tasa de Exito (%)</h2>
          <p className="text-sm text-slate-400">Tendencia mensual</p>
          <div className="mt-8 flex h-56 items-end gap-4">
            {metricsSnapshot.successTrend.map((value, index) => (
              <div key={`${value}-${index}`} className="flex flex-1 flex-col items-center gap-3">
                <div className="w-full rounded-t-2xl bg-emerald-400" style={{ height: `${value * 1.6}px` }} />
                <span className="text-[11px] text-slate-300">{89 + index}%</span>
              </div>
            ))}
          </div>
        </SurfaceCard>
      </div>

      <div className="grid gap-5 xl:grid-cols-[0.8fr_1fr_1fr]">
        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Errores por Tipo</h2>
          <div className="mt-8 flex justify-center">
            <div className="grid h-44 w-44 place-items-center rounded-full bg-[conic-gradient(#ef4444_0_35%,#f59e0b_35%_63%,#3b82f6_63%_83%,#8b5cf6_83%_95%,rgba(226,232,240,0.8)_95%_100%)]">
              <div className="grid h-28 w-28 place-items-center rounded-full bg-white text-center">
                <div>
                  <p className="text-4xl font-bold text-brand-blue">72</p>
                  <p className="text-xs text-slate-400">total</p>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-6 space-y-3 text-sm text-slate-500">
            {[
              ['Timeout', '35%', 'bg-red-500'],
              ['Conexion', '28%', 'bg-amber-500'],
              ['Datos', '20%', 'bg-blue-500'],
              ['Interfaz', '12%', 'bg-violet-500'],
              ['Credenciales', '5%', 'bg-slate-400'],
            ].map(([label, percent, color]) => (
              <div key={label} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
                  {label}
                </div>
                <span>{percent}</span>
              </div>
            ))}
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">RPA con Mas Fallas</h2>
          <p className="text-sm text-slate-400">Top 6 del mes</p>
          <div className="mt-6 space-y-5">
            {metricsSnapshot.topFailures.map((item) => (
              <div key={item.name}>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="font-medium text-brand-blue">{item.name}</span>
                  <span className="font-semibold text-brand-blue">{item.value}</span>
                </div>
                <div className="h-3 rounded-full bg-slate-100">
                  <div
                    className={`h-full rounded-full ${item.tone === 'red' ? 'bg-red-500' : item.tone === 'amber' ? 'bg-amber-500' : 'bg-emerald-500'}`}
                    style={{ width: `${Math.min(100, item.value * 3)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Tiempo Promedio por RPA</h2>
          <p className="text-sm text-slate-400">En minutos</p>
          <div className="mt-6 space-y-5">
            {metricsSnapshot.averageByRpa.map((item) => (
              <div key={item.name}>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="font-medium text-brand-blue">{item.name}</span>
                  <span className="font-semibold text-blue-500">{item.value}m</span>
                </div>
                <div className="h-3 rounded-full bg-slate-100">
                  <div className="h-full rounded-full bg-blue-300" style={{ width: `${item.value * 10}%` }} />
                </div>
              </div>
            ))}
          </div>
        </SurfaceCard>
      </div>
    </div>
  )
}
