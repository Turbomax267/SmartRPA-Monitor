import { ArrowLeft, ClipboardPenLine, PlayCircle } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { AppBadge } from '../components/common/AppBadge'
import { Breadcrumbs } from '../components/common/Breadcrumbs'
import { CircularMeter } from '../components/common/CircularMeter'
import { SurfaceCard } from '../components/common/SurfaceCard'
import { getAnalysisById, getIncidentById } from '../mocks/monitorData'

export function IncidentDetailPage() {
  const { incidentId } = useParams()
  const incident = getIncidentById(incidentId)
  const analysis = getAnalysisById(incident.analysisId)

  return (
    <div className="space-y-6">
      <div>
        <Breadcrumbs items={[{ label: 'Alertas e Incidentes', to: '/incidents' }, { label: 'Detalle' }]} />
        <div className="flex flex-wrap items-center gap-4">
          <h1 className="text-4xl font-bold tracking-tight text-brand-blue">
            {incident.code} - {incident.title}
          </h1>
          <AppBadge tone="blue">En revision</AppBadge>
          <AppBadge tone="red">Alta</AppBadge>
          <AppBadge tone="amber">{incident.category}</AppBadge>
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.55fr_0.95fr]">
        <div className="space-y-5">
          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Informacion general</h2>
            <div className="mt-6 grid gap-5 md:grid-cols-2">
              {[
                ['Codigo', incident.code],
                ['RPA afectado', incident.rpaName],
                ['Ejecucion asociada', incident.executionCode],
                ['Responsable asignado', incident.responsible],
                ['Fecha de deteccion', incident.detectedAt],
                ['Ultima actualizacion', incident.updatedAt],
                ['Estado', 'En revision'],
                ['Criticidad', 'Alta'],
              ].map(([label, value]) => (
                <div key={label}>
                  <p className="text-sm font-semibold text-slate-400">{label}</p>
                  <p className="mt-1 text-lg font-semibold text-brand-blue">{value}</p>
                </div>
              ))}
            </div>
          </SurfaceCard>

          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Descripcion del incidente</h2>
            <p className="mt-4 text-base leading-8 text-slate-500">{incident.description}</p>
          </SurfaceCard>

          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Causa probable</h2>
            <p className="mt-4 text-base leading-8 text-slate-500">{incident.probableCause}</p>
          </SurfaceCard>

          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Seguimiento tecnico</h2>
            <div className="mt-6 space-y-4">
              {incident.timeline.map((step) => (
                <div key={`${step.at}-${step.action}`} className="grid grid-cols-[0.9fr_0.9fr_0.8fr_1.3fr] gap-4 rounded-2xl bg-slate-50 px-4 py-4 text-sm text-slate-500">
                  <span>{step.at}</span>
                  <span>{step.user}</span>
                  <AppBadge
                    tone={
                      step.action === 'ASSIGNMENT'
                        ? 'blue'
                        : step.action === 'COMMENT'
                          ? 'slate'
                          : step.action === 'TECHNICAL_ACTION'
                            ? 'amber'
                            : 'green'
                    }
                    className="w-fit"
                  >
                    {step.action}
                  </AppBadge>
                  <span>{step.comment}</span>
                </div>
              ))}
            </div>
          </SurfaceCard>
        </div>

        <div className="space-y-5">
          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Datos relacionados</h2>
            <div className="mt-6 space-y-4 text-sm text-slate-500">
              <div className="flex justify-between">
                <span className="font-semibold text-brand-blue">Tipo de error:</span>
                <span>{incident.category}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-brand-blue">Bot:</span>
                <span>{incident.rpaName}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-brand-blue">Ejecucion:</span>
                <span>{incident.executionCode}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-brand-blue">Fecha deteccion:</span>
                <span>{incident.detectedAt}</span>
              </div>
            </div>
          </SurfaceCard>

          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Estado del incidente</h2>
            <div className="mt-6 space-y-4">
              {[
                { label: 'Detectado', value: incident.detectedAt, active: true },
                { label: 'En revision', value: incident.updatedAt, active: true },
                { label: 'Resuelto', value: '-', active: false },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className={`h-4 w-4 rounded-full border-2 ${item.active ? 'border-blue-500 bg-blue-500' : 'border-slate-300'}`} />
                    <span className={`font-semibold ${item.active ? 'text-brand-blue' : 'text-slate-400'}`}>{item.label}</span>
                  </div>
                  <span className="text-sm text-slate-400">{item.value}</span>
                </div>
              ))}
            </div>
          </SurfaceCard>

          <SurfaceCard>
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-brand-blue">Analisis con IA</h2>
              <AppBadge tone="purple">IA</AppBadge>
            </div>
            <div className="mt-6 space-y-4 text-sm text-slate-500">
              <div className="flex justify-between">
                <span className="font-semibold text-brand-blue">Clasificacion:</span>
                <span>{analysis.classification}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-semibold text-brand-blue">Confianza:</span>
                <CircularMeter value={analysis.confidence} label="confianza" size={92} />
              </div>
              <div>
                <p className="font-semibold text-brand-blue">Posible causa:</p>
                <p className="mt-2 leading-7">{analysis.probableCause}</p>
              </div>
              <div>
                <p className="font-semibold text-brand-blue">Recomendacion:</p>
                <p className="mt-2 leading-7">{analysis.recommendation[0]}</p>
              </div>
            </div>
            <Link
              to={`/ai-analysis/${analysis.id}`}
              className="mt-6 inline-flex w-full items-center justify-center rounded-2xl border border-brand-blue/15 px-4 py-3 text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5"
            >
              Ver analisis completo
            </Link>
          </SurfaceCard>

          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Resolucion</h2>
            <div className="mt-5 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 p-5 text-sm text-slate-500">
              {incident.resolution || 'Aun no se registra una resolucion para este incidente.'}
            </div>
          </SurfaceCard>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-4">
        <button className="rounded-2xl bg-brand-blue px-5 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(4,35,84,0.18)] transition hover:-translate-y-0.5">
          Actualizar estado
        </button>
        <button className="rounded-2xl border border-brand-blue/15 bg-white px-5 py-4 text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5">
          <span className="inline-flex items-center gap-2">
            <ClipboardPenLine size={18} />
            Agregar seguimiento
          </span>
        </button>
        <Link
          to={`/executions/${incident.executionId}`}
          className="rounded-2xl border border-brand-blue/15 bg-white px-5 py-4 text-center text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5"
        >
          <span className="inline-flex items-center gap-2">
            <PlayCircle size={18} />
            Ver ejecucion
          </span>
        </Link>
        <Link
          to="/incidents"
          className="rounded-2xl border border-brand-blue/15 bg-white px-5 py-4 text-center text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5"
        >
          <span className="inline-flex items-center gap-2">
            <ArrowLeft size={18} />
            Volver a alertas
          </span>
        </Link>
      </div>
    </div>
  )
}
