import { AlertTriangle, Bot, ChartNoAxesCombined, CircleOff, Clock3, Gauge, ShieldCheck } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart, CartesianGrid } from 'recharts'
import { dashboardSummaryRequest } from '../api/dashboard.api'
import { StatCard } from '../components/dashboard/StatCard'
import type { DashboardSummary } from '../interfaces'
import { formatDateLabel, formatDuration, formatNumber, formatPercent } from '../utils/format'

const errorColors = ['#EF4444', '#F59E0B', '#3B82F6', '#22C55E', '#6B7280']

export function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setIsLoading(true)
        const response = await dashboardSummaryRequest()
        setSummary(response.data)
      } catch {
        setError('No pudimos cargar el dashboard en este momento.')
      } finally {
        setIsLoading(false)
      }
    }

    void fetchSummary()
  }, [])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-brand-blue">Resumen General</h1>
          <p className="mt-2 text-sm text-slate-400">Cargando información del sistema...</p>
        </div>
        <div className="grid gap-5 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, index) => (
            <div key={index} className="h-36 animate-pulse rounded-3xl bg-white shadow-soft" />
          ))}
        </div>
      </div>
    )
  }

  if (error || !summary) {
    return (
      <div className="rounded-3xl border border-red-100 bg-white p-10 shadow-soft">
        <p className="text-xl font-semibold text-brand-blue">No se pudo cargar el dashboard</p>
        <p className="mt-2 text-sm text-slate-500">{error ?? 'Inténtalo nuevamente más tarde.'}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-brand-blue">Resumen General</h1>
        <p className="mt-2 text-sm text-slate-400">
          Estado actual de todos los procesos RPA registrados
        </p>
      </div>

      <div className="grid gap-5 xl:grid-cols-4">
        <StatCard
          title="Total RPA"
          value={formatNumber(summary.total_rpas)}
          subtitle="Bots monitoreados"
          accent="bg-brand-info"
          icon={<Bot size={20} />}
        />
        <StatCard
          title="RPA Activos"
          value={formatNumber(summary.active_rpas)}
          subtitle="En ejecución normal"
          accent="bg-brand-success"
          icon={<ShieldCheck size={20} />}
        />
        <StatCard
          title="RPA Inactivos"
          value={formatNumber(summary.inactive_rpas)}
          subtitle="Sin ejecuciones"
          accent="bg-slate-300"
          icon={<CircleOff size={20} />}
        />
        <StatCard
          title="En Revisión"
          value={formatNumber(summary.under_review_rpas)}
          subtitle="Requieren atención"
          accent="bg-brand-warning"
          icon={<AlertTriangle size={20} />}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-4">
        <StatCard
          title="Total Ejecuciones"
          value={formatNumber(summary.total_executions)}
          subtitle="Histórico disponible"
          accent="bg-brand-info"
          icon={<ChartNoAxesCombined size={20} />}
        />
        <StatCard
          title="Tasa de Éxito"
          value={formatPercent(summary.success_rate)}
          subtitle="Rendimiento general"
          accent="bg-brand-success"
          icon={<Gauge size={20} />}
        />
        <StatCard
          title="Errores Detectados"
          value={formatNumber(summary.detected_errors)}
          subtitle="Incidentes y fallos"
          accent="bg-brand-error"
          icon={<AlertTriangle size={20} />}
        />
        <StatCard
          title="Tiempo Promedio"
          value={formatDuration(summary.average_duration_ms)}
          subtitle="Por ejecución"
          accent="bg-brand-warning"
          icon={<Clock3 size={20} />}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.6fr_1fr]">
        <div className="rounded-3xl bg-white p-6 shadow-soft">
          <h3 className="text-xl font-semibold text-brand-blue">Ejecuciones por día</h3>
          <p className="mb-6 text-sm text-slate-400">Últimos 14 días</p>

          <div className="h-80">
            {summary.executions_by_day.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-slate-400">
                No hay registros de ejecuciones todavía.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={summary.executions_by_day}>
                  <CartesianGrid vertical={false} stroke="#E8EAF0" />
                  <XAxis dataKey="day" tick={{ fill: '#6B7280', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#6B7280', fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="total" radius={[12, 12, 0, 0]} fill="#042354" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="rounded-3xl bg-white p-6 shadow-soft">
          <h3 className="text-xl font-semibold text-brand-blue">Errores por categoría</h3>
          <p className="mb-6 text-sm text-slate-400">Distribución actual</p>

          <div className="h-80">
            {summary.errors_by_category.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-slate-400">
                No hay errores registrados.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={summary.errors_by_category}
                    dataKey="total"
                    nameKey="category"
                    cx="50%"
                    cy="46%"
                    innerRadius={68}
                    outerRadius={92}
                    paddingAngle={3}
                  >
                    {summary.errors_by_category.map((entry, index) => (
                      <Cell key={`${entry.category}-${index}`} fill={errorColors[index % errorColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="space-y-2">
            {summary.errors_by_category.map((entry, index) => (
              <div key={`${entry.category}-${index}`} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2 text-slate-500">
                  <span
                    className="h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: errorColors[index % errorColors.length] }}
                  />
                  {entry.category}
                </div>
                <span className="font-semibold text-brand-blue">{formatNumber(entry.total)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-3xl bg-white p-6 shadow-soft">
        <h3 className="text-xl font-semibold text-brand-blue">Últimas Ejecuciones</h3>
        <p className="mb-6 text-sm text-slate-400">Trazabilidad operativa reciente</p>

        <div className="overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-y-3">
            <thead>
              <tr className="text-left text-sm text-slate-400">
                <th className="pb-2">RPA</th>
                <th className="pb-2">Proceso</th>
                <th className="pb-2">Estado</th>
                <th className="pb-2">Duración</th>
                <th className="pb-2">Responsable</th>
                <th className="pb-2">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {summary.latest_executions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="rounded-2xl bg-slate-50 px-4 py-8 text-center text-sm text-slate-400">
                    Todavía no existen ejecuciones para mostrar.
                  </td>
                </tr>
              ) : (
                summary.latest_executions.map((execution) => (
                  <tr key={execution.id} className="rounded-2xl bg-slate-50 text-sm text-slate-600">
                    <td className="rounded-l-2xl px-4 py-4 font-semibold text-brand-blue">{execution.rpa ?? '-'}</td>
                    <td className="px-4 py-4">{execution.process ?? '-'}</td>
                    <td className="px-4 py-4">
                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                          execution.status === 'SUCCESS'
                            ? 'bg-emerald-100 text-emerald-600'
                            : execution.status === 'FAILED'
                              ? 'bg-red-100 text-red-500'
                              : 'bg-amber-100 text-amber-600'
                        }`}
                      >
                        {execution.status === 'SUCCESS'
                          ? 'Exitoso'
                          : execution.status === 'FAILED'
                            ? 'Fallido'
                            : 'En revisión'}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      {execution.duration_ms ? formatDuration(execution.duration_ms) : '-'}
                    </td>
                    <td className="px-4 py-4">{execution.responsible ?? '-'}</td>
                    <td className="rounded-r-2xl px-4 py-4">{formatDateLabel(execution.started_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
