import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { listIncidentsRequest } from '../api/monitor.api'
import { AppBadge } from '../components/common/AppBadge'
import { SurfaceCard } from '../components/common/SurfaceCard'

const tabs = ['Todas', 'Pendientes', 'En revision', 'Resueltas', 'Observadas'] as const

export function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>([])
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]>('Todas')

  useEffect(() => {
    const load = async () => {
      const response = await listIncidentsRequest()
      setIncidents(response.data)
    }

    void load()
  }, [])

  const filteredIncidents = useMemo(() => {
    if (activeTab === 'Todas') {
      return incidents
    }

    return incidents.filter((item) => {
      if (activeTab === 'Pendientes') return item.status === 'PENDING'
      if (activeTab === 'En revision') return item.status === 'IN_REVIEW'
      if (activeTab === 'Resueltas') return item.status === 'RESOLVED'
      return item.status === 'OBSERVED'
    })
  }, [activeTab, incidents])

  const counters = {
    total: incidents.length,
    pending: incidents.filter((item) => item.status === 'PENDING').length,
    review: incidents.filter((item) => item.status === 'IN_REVIEW').length,
    resolved: incidents.filter((item) => item.status === 'RESOLVED').length,
    observed: incidents.filter((item) => item.status === 'OBSERVED').length,
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-brand-blue">Alertas e Incidentes</h1>
        <p className="mt-2 text-lg text-brand-blue">Control y gestion de fallas detectadas en el sistema RPA</p>
      </div>

      <div className="grid gap-4 xl:grid-cols-5">
        {[
          ['Total Alertas', counters.total, 'red'],
          ['Pendientes', counters.pending, 'amber'],
          ['En Revision', counters.review, 'blue'],
          ['Resueltas', counters.resolved, 'green'],
          ['Observadas', counters.observed, 'slate'],
        ].map(([label, value, tone]) => (
          <SurfaceCard key={label} className="p-5">
            <div className={`mb-4 h-1 w-full rounded-full ${tone === 'red' ? 'bg-red-400' : tone === 'amber' ? 'bg-amber-400' : tone === 'blue' ? 'bg-blue-400' : tone === 'green' ? 'bg-emerald-400' : 'bg-slate-300'}`} />
            <p className="text-5xl font-bold text-brand-blue">{value}</p>
            <p className={`mt-3 text-sm font-semibold ${tone === 'red' ? 'text-red-500' : tone === 'amber' ? 'text-amber-500' : tone === 'blue' ? 'text-blue-500' : tone === 'green' ? 'text-emerald-500' : 'text-slate-500'}`}>
              {label}
            </p>
          </SurfaceCard>
        ))}
      </div>

      <div className="flex flex-wrap gap-3">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`rounded-full px-5 py-3 text-sm font-semibold transition ${
              activeTab === tab
                ? 'bg-brand-blue text-white shadow-[0_12px_24px_rgba(4,35,84,0.18)]'
                : 'bg-white text-slate-400 shadow-soft hover:text-brand-blue'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <SurfaceCard className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left">
            <thead className="bg-brand-blue text-sm text-white">
              <tr>
                {['Codigo', 'RPA Afectado', 'Tipo de Error', 'Criticidad', 'Estado', 'Fecha', 'Responsable', 'Acciones'].map((label) => (
                  <th key={label} className="px-4 py-4">
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredIncidents.map((incident) => (
                <tr key={incident.id} className="border-b border-slate-100 text-sm text-slate-500 transition hover:bg-slate-50/80">
                  <td className="px-4 py-4 font-semibold text-brand-info">{incident.code}</td>
                  <td className="px-4 py-4">{incident.rpaName}</td>
                  <td className="px-4 py-4">{incident.category}</td>
                  <td className="px-4 py-4">
                    <AppBadge tone={incident.severity === 'HIGH' ? 'red' : incident.severity === 'MEDIUM' ? 'amber' : 'green'}>
                      {incident.severity === 'HIGH' ? 'Alta' : incident.severity === 'MEDIUM' ? 'Media' : 'Baja'}
                    </AppBadge>
                  </td>
                  <td className="px-4 py-4">
                    <AppBadge
                      tone={
                        incident.status === 'PENDING'
                          ? 'amber'
                          : incident.status === 'IN_REVIEW'
                            ? 'blue'
                            : incident.status === 'RESOLVED'
                              ? 'green'
                              : 'slate'
                      }
                    >
                      {incident.status === 'PENDING'
                        ? 'Pendiente'
                        : incident.status === 'IN_REVIEW'
                          ? 'En revision'
                          : incident.status === 'RESOLVED'
                            ? 'Resuelto'
                            : 'Observado'}
                    </AppBadge>
                  </td>
                  <td className="px-4 py-4">{incident.detectedAt}</td>
                  <td className="px-4 py-4">{incident.responsible}</td>
                  <td className="px-4 py-4">
                    <div className="flex gap-2">
                      <Link
                        to={`/executions/${incident.executionId}`}
                        className="rounded-xl bg-blue-50 px-3 py-2 text-xs font-semibold text-blue-600"
                      >
                        Ver
                      </Link>
                      <Link
                        to={`/incidents/${incident.id}`}
                        className="rounded-xl bg-slate-100 px-3 py-2 text-xs font-semibold text-brand-blue"
                      >
                        Detalle
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SurfaceCard>
    </div>
  )
}
