import { ArrowRight, Bot, Play, ShieldCheck } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getRpaRequest } from '../api/monitor.api'
import type {
  IncidentDetail,
  RpaDetail,
  RpaExecutionSummary,
  RpaIncidentBreakdownItem,
  RpaInfoItem,
  RpaRecentHistoryItem,
} from '../api/monitor.api'
import { AppBadge } from '../components/common/AppBadge'
import { Breadcrumbs } from '../components/common/Breadcrumbs'
import { SurfaceCard } from '../components/common/SurfaceCard'

export function RpaDetailPage() {
  const { rpaId } = useParams()
  const [rpa, setRpa] = useState<RpaDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'Resumen' | 'Ejecuciones' | 'Incidentes'>('Resumen')

  const relatedExecutions = useMemo(
    () => (rpa?.executions ?? []).slice(0, 5),
    [rpa],
  )
  const relatedIncidents = useMemo(
    () => (rpa?.incidents ?? []).slice(0, 5),
    [rpa],
  )

  useEffect(() => {
    const load = async () => {
      if (!rpaId) {
        setError('No se encontro el identificador del RPA.')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError(null)
        const response = await getRpaRequest(rpaId)
        setRpa(response.data)
      } catch {
        setError('No se pudo cargar el detalle del RPA.')
      } finally {
        setLoading(false)
      }
    }

    void load()
  }, [rpaId])

  if (loading) {
    return <div className="text-sm text-slate-400">Cargando RPA...</div>
  }

  if (error || !rpa) {
    return <div className="text-sm text-red-500">{error ?? 'No se pudo cargar el RPA.'}</div>
  }

  const lifecycleTone =
    rpa.lifecycleStatus === 'ACTIVE'
      ? 'green'
      : rpa.lifecycleStatus === 'MAINTENANCE' || rpa.lifecycleStatus === 'UNDER_REVIEW'
        ? 'amber'
        : rpa.lifecycleStatus === 'INACTIVE'
          ? 'slate'
          : 'red'

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-6">
        <div>
          <Breadcrumbs items={[{ label: 'RPA / Bots', to: '/rpas' }, { label: 'Detalle' }]} />
          <div className="flex flex-wrap items-center gap-4">
            <h1 className="text-4xl font-bold tracking-tight text-brand-blue">{rpa.name}</h1>
            <AppBadge tone={lifecycleTone}>
              {rpa.lifecycleStatus === 'ACTIVE'
                ? 'Activo'
                : rpa.lifecycleStatus === 'MAINTENANCE' || rpa.lifecycleStatus === 'UNDER_REVIEW'
                  ? 'En revision'
                  : rpa.lifecycleStatus === 'INACTIVE'
                    ? 'Inactivo'
                    : 'Error'}
            </AppBadge>
            <AppBadge tone="blue">Proceso</AppBadge>
            <AppBadge tone="slate">{rpa.processName}</AppBadge>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button className="rounded-2xl bg-brand-blue px-6 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(4,35,84,0.18)] transition hover:-translate-y-0.5">
            <span className="inline-flex items-center gap-2">
              <Play size={16} />
              Ejecutar
            </span>
          </button>
          <button className="rounded-2xl border border-slate-200 bg-white px-6 py-4 text-sm font-semibold text-brand-blue transition hover:border-brand-blue/20 hover:bg-brand-blue/5">
            Editar
          </button>
          <Link
            to="/executions"
            className="rounded-2xl border border-slate-200 bg-white px-6 py-4 text-sm font-semibold text-brand-blue transition hover:border-brand-blue/20 hover:bg-brand-blue/5"
          >
            Ver ejecuciones
          </Link>
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.45fr_1fr]">
        <SurfaceCard>
          <div className="grid gap-6 md:grid-cols-[180px_1fr]">
            <div className="grid place-items-center rounded-[2rem] bg-[radial-gradient(circle_at_top,_rgba(230,238,255,1),_rgba(244,246,252,1)_65%)] p-6">
              <Bot size={88} className="text-brand-blue" />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {[
                ['Codigo', rpa.code],
                ['Proceso', rpa.processName],
                ['Responsable', rpa.responsible],
                ['Script', rpa.scriptName],
                ['Modo de ejecucion', rpa.executionMode],
                ['Agente asignado', rpa.assignedAgent],
                ['Ultima ejecucion', rpa.lastExecutionLabel],
              ].map(([label, value]) => (
                <div key={label}>
                  <p className="text-sm font-semibold text-slate-400">{label}</p>
                  <p className="mt-1 text-lg font-semibold text-brand-blue">{value}</p>
                </div>
              ))}
            </div>
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-brand-blue">Estado del bot</h2>
            <AppBadge tone={rpa.agentStatus === 'ONLINE' ? 'green' : 'slate'}>
              {rpa.agentStatus === 'ONLINE' ? 'Agente online' : 'Agente offline'}
            </AppBadge>
          </div>

          <div className="mt-6 space-y-4 text-sm text-slate-500">
            <div className="flex items-center justify-between">
              <span>Agente conectado</span>
              <span className="font-semibold text-brand-blue">{rpa.assignedAgent} (v2.4.1)</span>
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between">
                <span>Uptime</span>
                <span className="font-semibold text-brand-blue">{rpa.uptime}%</span>
              </div>
              <div className="h-2.5 rounded-full bg-slate-100">
                <div className="h-full rounded-full bg-emerald-500" style={{ width: `${rpa.uptime}%` }} />
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span>Entorno</span>
              <span className="font-semibold text-brand-blue">{rpa.environment}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Proxima ejecucion</span>
              <span className="font-semibold text-brand-blue">{rpa.nextExecution}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Frecuencia</span>
              <span className="font-semibold text-brand-blue">{rpa.frequency}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Tiempo desde ultima ejecucion</span>
              <span className="font-semibold text-brand-blue">{rpa.sinceLastRun}</span>
            </div>
          </div>
        </SurfaceCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-4">
        {[
          {
            label: 'Ejecuciones exitosas',
            value: rpa.stats.successfulExecutions.toLocaleString('es-PE'),
            tone: 'green',
            helper: '+ 12.4% vs. periodo anterior',
          },
          { label: 'Incidentes', value: `${rpa.stats.incidents}`, tone: 'red', helper: '+ 8.1% vs. periodo anterior' },
          { label: 'Tiempo promedio', value: `${rpa.stats.averageMinutes} min`, tone: 'blue', helper: '- 0.3 min vs. periodo anterior' },
          { label: 'Tasa de exito', value: `${rpa.stats.successRate}%`, tone: 'amber', helper: '+ 3.7 pp vs. periodo anterior' },
        ].map((stat) => (
          <SurfaceCard key={stat.label}>
            <p className={`text-4xl font-bold ${stat.tone === 'green' ? 'text-emerald-500' : stat.tone === 'red' ? 'text-red-500' : stat.tone === 'blue' ? 'text-blue-500' : 'text-amber-500'}`}>
              {stat.value}
            </p>
            <p className="mt-2 text-lg font-semibold text-brand-blue">{stat.label}</p>
            <p className="text-sm text-slate-400">{stat.helper}</p>
          </SurfaceCard>
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.15fr_1fr]">
        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Incidentes frecuentes</h2>
          <div className="mt-6 space-y-5">
            {rpa.incidentBreakdown.map((item: RpaIncidentBreakdownItem) => (
              <div key={item.label}>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <div>
                    <p className="font-semibold text-brand-blue">{item.label}</p>
                    <p className="text-slate-400">{item.total} casos</p>
                  </div>
                  <span className="font-semibold text-brand-blue">{item.percent}%</span>
                </div>
                <div className="h-3 rounded-full bg-slate-100">
                  <div
                    className={`h-full rounded-full ${
                      item.tone === 'red'
                        ? 'bg-red-500'
                        : item.tone === 'amber'
                          ? 'bg-amber-500'
                          : item.tone === 'yellow'
                            ? 'bg-yellow-400'
                            : 'bg-slate-400'
                    }`}
                    style={{ width: `${item.percent}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
          <p className="mt-5 text-lg font-semibold text-brand-blue">
            Total de incidentes <span className="ml-3">{rpa.incidentBreakdown.reduce((sum: number, item: RpaIncidentBreakdownItem) => sum + item.total, 0)}</span>
          </p>
        </SurfaceCard>

        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Historial reciente</h2>
          <div className="mt-6 space-y-4">
            {rpa.recentHistory.map((item: RpaRecentHistoryItem) => (
              <div key={item.label} className="grid grid-cols-[1.2fr_0.75fr_0.75fr_1fr] gap-3 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-500">
                <span>{item.label}</span>
                <AppBadge tone={item.status === 'SUCCESS' ? 'green' : 'red'} className="w-fit">
                  {item.status === 'SUCCESS' ? 'Exitosa' : 'Fallida'}
                </AppBadge>
                <span>{item.duration}</span>
                <span className="font-medium text-brand-blue">{item.result}</span>
              </div>
            ))}
          </div>
          <Link to="/executions" className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-brand-info">
            Ver todas las ejecuciones <ArrowRight size={16} />
          </Link>
        </SurfaceCard>
      </div>

      <SurfaceCard>
        <div className="flex items-center gap-8 border-b border-slate-100 pb-4">
          {(['Resumen', 'Ejecuciones', 'Incidentes'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`border-b-2 pb-3 text-base font-semibold transition ${
                activeTab === tab ? 'border-brand-info text-brand-info' : 'border-transparent text-slate-400'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {activeTab === 'Resumen' ? (
          <div className="mt-8 grid gap-8 xl:grid-cols-[1fr_1fr_320px]">
            <div>
              <h3 className="text-xl font-semibold text-brand-blue">Informacion tecnica</h3>
              <div className="mt-5 space-y-3">
                {rpa.technicalInfo.map((item: RpaInfoItem) => (
                  <div key={item.label} className="flex justify-between gap-4 rounded-2xl bg-slate-50 px-4 py-3 text-sm">
                    <span className="text-slate-400">{item.label}</span>
                    <span className="font-semibold text-brand-blue">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-brand-blue">Configuracion del RPA</h3>
              <div className="mt-5 space-y-3">
                {rpa.configurationInfo.map((item: RpaInfoItem) => (
                  <div key={item.label} className="flex justify-between gap-4 rounded-2xl bg-slate-50 px-4 py-3 text-sm">
                    <span className="text-slate-400">{item.label}</span>
                    <span className="font-semibold text-brand-blue">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-[26px] border border-dashed border-slate-200 bg-slate-50 p-6 text-center">
              <ShieldCheck size={34} className="mx-auto text-blue-500" />
              <h3 className="mt-4 text-xl font-semibold text-brand-blue">Buenas practicas</h3>
              <p className="mt-3 text-sm leading-6 text-slate-400">
                Este bot sigue las mejores practicas de desarrollo y operacion.
              </p>
              <button className="mt-6 rounded-2xl border border-brand-blue/10 bg-white px-4 py-3 text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5">
                Ver recomendaciones
              </button>
            </div>
          </div>
        ) : activeTab === 'Ejecuciones' ? (
          <div className="mt-8 space-y-3">
            {relatedExecutions.map((execution: RpaExecutionSummary) => (
              <Link
                key={execution.id}
                to={`/executions/${execution.id}`}
                className="grid grid-cols-[1.1fr_0.9fr_0.9fr_0.8fr_0.8fr] items-center gap-4 rounded-2xl bg-slate-50 px-5 py-4 text-sm text-slate-500 transition hover:-translate-y-0.5 hover:bg-white hover:shadow-soft"
              >
                <span className="font-semibold text-brand-blue">{execution.publicCode}</span>
                <AppBadge tone={execution.status === 'SUCCESS' ? 'green' : execution.status === 'FAILED' ? 'red' : 'amber'}>
                  {execution.status === 'SUCCESS' ? 'Exitosa' : execution.status === 'FAILED' ? 'Fallida' : 'Revision'}
                </AppBadge>
                <span>{execution.durationLabel}</span>
                <span>{execution.responsible}</span>
                <span>{execution.dateLabel}</span>
              </Link>
            ))}
          </div>
        ) : (
          <div className="mt-8 space-y-3">
            {relatedIncidents.length === 0 ? (
              <div className="rounded-2xl bg-slate-50 px-5 py-4 text-sm text-slate-400">No hay incidentes recientes para este RPA.</div>
            ) : relatedIncidents.map((incident: IncidentDetail) => (
              <Link
                key={incident.id}
                to={`/incidents/${incident.id}`}
                className="grid grid-cols-[1fr_0.8fr_0.8fr_0.8fr] items-center gap-4 rounded-2xl bg-slate-50 px-5 py-4 text-sm text-slate-500 transition hover:-translate-y-0.5 hover:bg-white hover:shadow-soft"
              >
                <span className="font-semibold text-brand-blue">{incident.code}</span>
                <AppBadge tone={incident.severity === 'HIGH' ? 'red' : incident.severity === 'MEDIUM' ? 'amber' : 'green'}>
                  {incident.severity === 'HIGH' ? 'Alta' : incident.severity === 'MEDIUM' ? 'Media' : 'Baja'}
                </AppBadge>
                <AppBadge tone={incident.status === 'RESOLVED' ? 'green' : incident.status === 'IN_REVIEW' ? 'blue' : incident.status === 'PENDING' ? 'amber' : 'slate'}>
                  {incident.status === 'RESOLVED' ? 'Resuelto' : incident.status === 'IN_REVIEW' ? 'En revision' : incident.status === 'PENDING' ? 'Pendiente' : 'Observado'}
                </AppBadge>
                <span>{incident.detectedAt}</span>
              </Link>
            ))}
          </div>
        )}
      </SurfaceCard>
    </div>
  )
}
