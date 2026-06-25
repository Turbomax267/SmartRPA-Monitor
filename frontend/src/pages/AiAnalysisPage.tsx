import { useEffect, useState } from 'react'
import { Copy, Info } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { getAnalysisRequest } from '../api/monitor.api'
import { AppBadge } from '../components/common/AppBadge'
import { Breadcrumbs } from '../components/common/Breadcrumbs'
import { CircularMeter } from '../components/common/CircularMeter'
import { SurfaceCard } from '../components/common/SurfaceCard'

export function AiAnalysisPage() {
  const { analysisId } = useParams()
  const [analysis, setAnalysis] = useState<any | null>(null)

  useEffect(() => {
    const load = async () => {
      if (!analysisId) return
      const response = await getAnalysisRequest(analysisId)
      setAnalysis(response.data)
    }

    void load()
  }, [analysisId])

  if (!analysis) {
    return <div className="text-sm text-slate-400">Cargando analisis...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <Breadcrumbs
          items={[
            { label: 'Ejecuciones', to: '/executions' },
            { label: 'Detalle de ejecucion', to: `/executions/${analysis.executionId}` },
            { label: 'Analisis con IA' },
          ]}
        />
        <h1 className="text-4xl font-bold tracking-tight text-brand-blue">Analisis con IA</h1>
      </div>

      <SurfaceCard>
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-semibold text-brand-blue">Contexto del analisis</h2>
          <Info size={18} className="text-brand-info" />
        </div>
        <div className="mt-6 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {[
            ['Codigo de ejecucion', analysis.executionCode],
            ['RPA', analysis.rpaName],
            ['Proceso', analysis.process],
            ['Fecha y hora', analysis.analyzedAt],
            ['Agente', analysis.agent],
            ['Incidente asociado', analysis.incidentId ?? 'Sin incidente'],
            ['Estado de ejecucion', analysis.executionStatus],
            ['Tipo de error preliminar', analysis.preliminaryError],
          ].map(([label, value]) => (
            <div key={label}>
              <p className="text-sm font-semibold text-slate-400">{label}</p>
              <p className="mt-2 text-lg font-semibold text-brand-blue">{value}</p>
            </div>
          ))}
        </div>
      </SurfaceCard>

      <div className="grid gap-5 xl:grid-cols-[1.55fr_0.95fr]">
        <div className="space-y-5">
          <SurfaceCard>
            <h3 className="text-2xl font-semibold text-brand-blue">A. Log analizado</h3>
            <div className="mt-5 rounded-[24px] bg-[#0b1220] px-5 py-5 font-mono text-sm text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">
              <div className="space-y-3">
                {analysis.sanitizedLog.map((line) => (
                  <div key={`${line.time}-${line.step}`} className="grid grid-cols-[86px_80px_80px_1fr_26px] gap-3">
                    <span className="text-slate-300">{line.time}</span>
                    <span className={line.level === 'INFO' ? 'text-emerald-400' : line.level === 'ERROR' ? 'text-red-400' : 'text-amber-400'}>
                      {line.level}
                    </span>
                    <span className="text-cyan-400">{line.step}</span>
                    <span>{line.message}</span>
                    <Copy size={16} className="text-slate-500" />
                  </div>
                ))}
              </div>
            </div>
          </SurfaceCard>

          <SurfaceCard>
            <h3 className="text-2xl font-semibold text-brand-blue">B. Clasificacion del incidente</h3>
            <p className="mt-3 text-sm text-slate-400">Clasificacion sugerida por IA</p>
            <AppBadge tone="red" className="mt-5 text-base">
              {analysis.classification}
            </AppBadge>
          </SurfaceCard>

          <SurfaceCard>
            <h3 className="text-2xl font-semibold text-brand-blue">C. Posible causa</h3>
            <p className="mt-4 text-base leading-8 text-slate-500">{analysis.probableCause}</p>
          </SurfaceCard>

          <SurfaceCard>
            <h3 className="text-2xl font-semibold text-brand-blue">D. Recomendacion inicial</h3>
            <div className="mt-4 space-y-4">
              {analysis.recommendation.map((item, index) => (
                <div key={item} className="flex gap-3 text-base text-slate-500">
                  <span className="mt-1 flex h-7 w-7 items-center justify-center rounded-full border border-emerald-200 bg-emerald-50 text-sm font-semibold text-emerald-500">
                    {index + 1}
                  </span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
            <div className="mt-6 rounded-[24px] border border-amber-200 bg-amber-50/70 px-5 py-4 text-sm leading-7 text-amber-700">
              Este analisis es una recomendacion generada por IA y debe ser validada por el equipo tecnico antes de aplicar cambios en produccion.
            </div>
          </SurfaceCard>
        </div>

        <div className="space-y-5">
          <SurfaceCard>
            <h3 className="text-2xl font-semibold text-brand-blue">F. Nivel de confianza</h3>
            <div className="mt-6">
              <CircularMeter value={analysis.confidence} label="confianza" sublabel="Confianza alta" />
            </div>
          </SurfaceCard>

          <SurfaceCard>
            <h3 className="text-2xl font-semibold text-brand-blue">G. Metadatos del analisis</h3>
            <div className="mt-6 space-y-4 text-sm text-slate-500">
              <div className="flex justify-between">
                <span>Modelo</span>
                <span className="font-semibold text-brand-blue">{analysis.model}</span>
              </div>
              <div className="flex justify-between">
                <span>Tiempo de analisis</span>
                <span className="font-semibold text-brand-blue">{analysis.durationSeconds} segundos</span>
              </div>
              <div className="flex justify-between">
                <span>Patrones revisados</span>
                <span className="font-semibold text-brand-blue">{analysis.reviewedPatterns} historicos</span>
              </div>
              <div className="flex justify-between">
                <span>Fecha de analisis</span>
                <span className="font-semibold text-brand-blue">{analysis.analyzedAt}</span>
              </div>
            </div>
          </SurfaceCard>

          <SurfaceCard>
            <h3 className="text-2xl font-semibold text-brand-blue">H. Relacion con el incidente</h3>
            <div className="mt-6 space-y-4 text-sm text-slate-500">
              <div className="flex justify-between">
                <span>Codigo</span>
                <span className="font-semibold text-brand-info">{analysis.incidentId?.toUpperCase()}</span>
              </div>
              <div className="flex justify-between">
                <span>Criticidad</span>
                <AppBadge tone="red">Alta</AppBadge>
              </div>
              <div className="flex justify-between">
                <span>Responsable</span>
                <span className="font-semibold text-brand-blue">{analysis.responsible}</span>
              </div>
            </div>
            <Link
              to={`/incidents/${analysis.incidentId}`}
              className="mt-6 inline-flex w-full items-center justify-center rounded-2xl border border-brand-blue/15 px-4 py-3 text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5"
            >
              Ver incidente
            </Link>
          </SurfaceCard>

          <SurfaceCard>
            <h3 className="text-2xl font-semibold text-brand-blue">I. Analisis previos del mismo bot</h3>
            <div className="mt-5 space-y-4">
              {analysis.similarCases.map((item) => (
                <div key={item.date} className="grid grid-cols-[0.9fr_1fr_0.6fr] gap-3 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-500">
                  <span>{item.date}</span>
                  <span>{item.errorType}</span>
                  <span className={item.match >= 80 ? 'font-semibold text-emerald-500' : 'font-semibold text-amber-500'}>
                    {item.match}%
                  </span>
                </div>
              ))}
            </div>
          </SurfaceCard>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <button className="rounded-2xl bg-brand-blue px-5 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(4,35,84,0.18)] transition hover:-translate-y-0.5">
          Guardar analisis
        </button>
        <Link
          to={`/incidents/${analysis.incidentId}`}
          className="rounded-2xl bg-red-500 px-5 py-4 text-center text-sm font-semibold text-white shadow-[0_18px_34px_rgba(239,68,68,0.16)] transition hover:-translate-y-0.5"
        >
          Crear incidente
        </Link>
        <Link
          to={`/executions/${analysis.executionId}`}
          className="rounded-2xl border border-brand-blue/15 bg-white px-5 py-4 text-center text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5"
        >
          Volver al detalle de ejecucion
        </Link>
      </div>
    </div>
  )
}
