import { ArrowLeft, OctagonAlert, ShieldAlert, Sparkles, RotateCcw } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { AppBadge } from '../components/common/AppBadge'
import { Breadcrumbs } from '../components/common/Breadcrumbs'
import { CircularMeter } from '../components/common/CircularMeter'
import { SurfaceCard } from '../components/common/SurfaceCard'
import { getAnalysisById, getExecutionById, getIncidentById } from '../mocks/monitorData'

export function ExecutionDetailPage() {
  const { executionId } = useParams()
  const execution = getExecutionById(executionId)
  const incident = getIncidentById(execution.incidentId)
  const analysis = getAnalysisById(execution.analysisId)

  return (
    <div className="space-y-6">
      <div>
        <Breadcrumbs items={[{ label: 'Ejecuciones', to: '/executions' }, { label: 'Detalle' }]} />
        <h1 className="text-4xl font-bold tracking-tight text-brand-blue">Detalle de Ejecucion</h1>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <h2 className="text-4xl font-bold text-brand-blue">
          {execution.publicCode} - {execution.rpaName}
        </h2>
        <AppBadge tone="red">Fallido</AppBadge>
        <AppBadge tone="amber">{execution.errorType}</AppBadge>
        <AppBadge tone="blue">{execution.triggerType}</AppBadge>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.55fr_0.95fr]">
        <SurfaceCard>
          <h3 className="text-2xl font-semibold text-brand-blue">Informacion general</h3>
          <div className="mt-6 grid gap-5 md:grid-cols-2">
            {[
              ['Codigo de ejecucion', execution.publicCode],
              ['RPA', execution.rpaName],
              ['Proceso', execution.process],
              ['Agente', execution.agent],
              ['Responsable', execution.responsible],
              ['Trigger', execution.triggerType],
              ['Escenario', execution.scenario],
              ['Fecha inicio', '05/06/2026 14:30'],
              ['Fecha fin', '05/06/2026 14:31'],
              ['Duracion', execution.durationLabel],
            ].map(([label, value]) => (
              <div key={label}>
                <p className="text-sm font-semibold text-slate-400">{label}</p>
                <p className="mt-1 text-lg font-semibold text-brand-blue">{value}</p>
              </div>
            ))}
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <h3 className="text-2xl font-semibold text-brand-blue">Resultado de la ejecucion</h3>
          <div className="mt-6 space-y-4 text-sm text-slate-500">
            {[
              ['Estado', 'Fallido'],
              ['Total items', `${execution.totalItems}`],
              ['Exitosos', `${execution.successItems}`],
              ['Fallidos', `${execution.failedItems}`],
              ['Codigo de error', execution.errorCode ?? '-'],
              ['Mensaje de error', execution.errorMessage ?? '-'],
            ].map(([label, value], index) => (
              <div key={label} className="flex items-center justify-between border-b border-slate-100 pb-4 last:border-none last:pb-0">
                <span className="font-semibold text-brand-blue">{label}:</span>
                {index === 0 ? <AppBadge tone="red">{value}</AppBadge> : <span>{value}</span>}
              </div>
            ))}
          </div>
        </SurfaceCard>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.55fr_0.95fr]">
        <div className="space-y-5">
          <SurfaceCard>
            <h3 className="text-2xl font-semibold text-brand-blue">Resumen del resultado</h3>
            <p className="mt-4 text-base leading-8 text-slate-500">{execution.summary}</p>
          </SurfaceCard>

          <SurfaceCard>
            <h3 className="text-2xl font-semibold text-brand-blue">Detalle de logs</h3>
            <div className="mt-5 overflow-hidden rounded-[24px] border border-slate-100">
              <table className="min-w-full text-left">
                <thead className="bg-slate-50 text-sm text-brand-blue">
                  <tr>
                    {['Hora', 'Nivel', 'Paso', 'Mensaje'].map((label) => (
                      <th key={label} className="px-4 py-4">
                        {label}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {execution.logs.map((log) => (
                    <tr key={`${log.time}-${log.step}`} className="border-t border-slate-100 text-sm text-slate-500">
                      <td className="px-4 py-4">{log.time}</td>
                      <td className="px-4 py-4">
                        <AppBadge
                          tone={
                            log.level === 'INFO'
                              ? 'blue'
                              : log.level === 'WARNING'
                                ? 'amber'
                                : log.level === 'ERROR'
                                  ? 'red'
                                  : 'red'
                          }
                        >
                          {log.level}
                        </AppBadge>
                      </td>
                      <td className="px-4 py-4 font-medium text-brand-blue">{log.step}</td>
                      <td className="px-4 py-4">{log.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-5 rounded-[24px] border border-red-200 bg-red-50/70 p-5">
              <div className="flex items-start gap-3">
                <OctagonAlert className="mt-1 text-red-500" />
                <div>
                  <h4 className="text-xl font-semibold text-brand-blue">Error detectado</h4>
                  <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
                    <AppBadge tone="red">{execution.errorCode}</AppBadge>
                    <AppBadge tone="amber">REGISTRO</AppBadge>
                    <span className="text-slate-500">{execution.errorMessage}</span>
                  </div>
                </div>
              </div>
            </div>
          </SurfaceCard>
        </div>

        <div className="space-y-5">
          <SurfaceCard>
            <h3 className="text-2xl font-semibold text-brand-blue">Incidente asociado</h3>
            <div className="mt-6 space-y-4 text-sm text-slate-500">
              <div className="flex justify-between">
                <span className="font-semibold text-brand-blue">Codigo:</span>
                <span>{incident.code}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-brand-blue">Estado:</span>
                <AppBadge tone="blue">En revision</AppBadge>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-brand-blue">Criticidad:</span>
                <AppBadge tone="red">Alta</AppBadge>
              </div>
            </div>
            <Link
              to={`/incidents/${incident.id}`}
              className="mt-6 inline-flex w-full items-center justify-center rounded-2xl border border-brand-blue/15 px-4 py-3 text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5"
            >
              Ver incidente
            </Link>
          </SurfaceCard>

          <SurfaceCard>
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-semibold text-brand-blue">Analisis con IA</h3>
              <AppBadge tone="purple">IA</AppBadge>
            </div>
            <div className="mt-6 space-y-5 text-sm text-slate-500">
              <div className="flex justify-between">
                <span className="font-semibold text-brand-blue">Clasificacion:</span>
                <span>{analysis.classification}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-semibold text-brand-blue">Confianza:</span>
                <CircularMeter value={analysis.confidence} label="confianza" size={92} />
              </div>
              <div>
                <p className="font-semibold text-brand-blue">Causa probable:</p>
                <p className="mt-2 leading-7">{analysis.probableCause}</p>
              </div>
            </div>
            <Link
              to={`/ai-analysis/${analysis.id}`}
              className="mt-6 inline-flex w-full items-center justify-center rounded-2xl border border-brand-blue/15 px-4 py-3 text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5"
            >
              Ver analisis completo
            </Link>
          </SurfaceCard>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-4">
        <button className="rounded-2xl bg-brand-blue px-5 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(4,35,84,0.18)] transition hover:-translate-y-0.5">
          <span className="inline-flex items-center gap-2">
            <RotateCcw size={18} />
            Reintentar ejecucion
          </span>
        </button>
        <Link
          to={`/incidents/${incident.id}`}
          className="rounded-2xl border border-brand-blue/15 bg-white px-5 py-4 text-center text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5"
        >
          <span className="inline-flex items-center gap-2">
            <ShieldAlert size={18} />
            Ver incidente
          </span>
        </Link>
        <Link
          to={`/ai-analysis/${analysis.id}`}
          className="rounded-2xl border border-brand-blue/15 bg-white px-5 py-4 text-center text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5"
        >
          <span className="inline-flex items-center gap-2">
            <Sparkles size={18} />
            Analizar con IA
          </span>
        </Link>
        <Link
          to="/executions"
          className="rounded-2xl border border-brand-blue/15 bg-white px-5 py-4 text-center text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5"
        >
          <span className="inline-flex items-center gap-2">
            <ArrowLeft size={18} />
            Volver a ejecuciones
          </span>
        </Link>
      </div>
    </div>
  )
}
