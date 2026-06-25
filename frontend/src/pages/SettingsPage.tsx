import { useState } from 'react'
import { AppBadge } from '../components/common/AppBadge'
import { SurfaceCard } from '../components/common/SurfaceCard'
import { settingsSnapshot } from '../mocks/monitorData'

export function SettingsPage() {
  const [selectedRefresh, setSelectedRefresh] = useState('1 min')
  const [selectedTimeout, setSelectedTimeout] = useState('5 min')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-brand-blue">Configuracion</h1>
        <p className="mt-2 text-lg text-brand-blue">Configuracion del Sistema</p>
        <p className="text-sm text-slate-400">Parametros generales de SmartRPA Monitor</p>
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Monitoreo y Ejecucion</h2>
          <div className="mt-6 space-y-5">
            <div>
              <p className="text-sm font-semibold text-brand-blue">Frecuencia de actualizacion del dashboard</p>
              <div className="mt-3 flex flex-wrap gap-3">
                {settingsSnapshot.refreshOptions.map((option) => (
                  <button
                    key={option}
                    onClick={() => setSelectedRefresh(option)}
                    className={`rounded-2xl px-6 py-3 text-sm font-semibold transition ${
                      selectedRefresh === option ? 'bg-brand-blue text-white shadow-soft' : 'bg-slate-100 text-slate-500'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <p className="text-sm font-semibold text-brand-blue">Timeout para agente desconectado</p>
              <div className="mt-3 flex flex-wrap gap-3">
                {settingsSnapshot.timeoutOptions.map((option) => (
                  <button
                    key={option}
                    onClick={() => setSelectedTimeout(option)}
                    className={`rounded-2xl px-6 py-3 text-sm font-semibold transition ${
                      selectedTimeout === option ? 'bg-brand-blue text-white shadow-soft' : 'bg-slate-100 text-slate-500'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>
            <p className="text-sm text-slate-400">
              Define cada cuanto se consulta el estado de ejecuciones y agentes RPA.
            </p>
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Canales de alerta</h2>
          <div className="mt-6 space-y-3">
            {settingsSnapshot.channels.map((channel) => (
              <div key={channel.label} className="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50 px-4 py-4">
                <div>
                  <p className="font-semibold text-brand-blue">{channel.label}</p>
                </div>
                <div className="flex items-center gap-4">
                  <AppBadge tone={channel.active ? 'green' : 'slate'}>{channel.active ? 'Activo' : 'Inactivo'}</AppBadge>
                  <button className={`h-7 w-14 rounded-full ${channel.active ? 'bg-brand-blue' : 'bg-slate-200'}`}>
                    <span className={`block h-6 w-6 rounded-full bg-white shadow transition ${channel.active ? 'translate-x-7' : 'translate-x-0.5'}`} />
                  </button>
                </div>
              </div>
            ))}
          </div>
          <p className="mt-4 text-sm text-slate-400">
            Los canales activos se usan para notificar incidentes criticos y fallas de ejecucion.
          </p>
        </SurfaceCard>

        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Categorias de incidentes</h2>
          <div className="mt-6 flex flex-wrap gap-3">
            {settingsSnapshot.categories.map((category) => (
              <AppBadge
                key={category.label}
                tone={
                  category.tone === 'blue'
                    ? 'blue'
                    : category.tone === 'purple'
                      ? 'purple'
                      : category.tone === 'amber'
                        ? 'amber'
                        : category.tone === 'green'
                          ? 'green'
                          : 'red'
                }
                className="px-4 py-2 text-sm"
              >
                {category.label}
              </AppBadge>
            ))}
          </div>
          <p className="mt-4 text-sm text-slate-400">
            Clasificacion utilizada para alertas, incidentes y analisis con IA.
          </p>
        </SurfaceCard>

        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Parametros de analisis con IA</h2>
          <div className="mt-6 space-y-4 text-sm text-slate-500">
            <div className="flex justify-between rounded-2xl bg-slate-50 px-4 py-3">
              <span>Proveedor</span>
              <span className="font-semibold text-brand-blue">Gemini API</span>
            </div>
            <div className="flex justify-between rounded-2xl bg-slate-50 px-4 py-3">
              <span>Modelo</span>
              <span className="font-semibold text-brand-blue">SmartRPA-IA v2.1</span>
            </div>
            <div className="flex justify-between rounded-2xl bg-slate-50 px-4 py-3">
              <span>Estado</span>
              <AppBadge tone="green">Activo</AppBadge>
            </div>
            <div className="flex justify-between rounded-2xl bg-slate-50 px-4 py-3">
              <span>Umbral de confianza</span>
              <span className="font-semibold text-brand-blue">80%</span>
            </div>
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Retencion de informacion</h2>
          <div className="mt-6 space-y-3">
            {[
              ['Logs de ejecucion', '90 dias'],
              ['Ejecuciones', '180 dias'],
              ['Incidentes', '365 dias'],
            ].map(([label, value]) => (
              <div key={label} className="flex justify-between rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-500">
                <span>{label}</span>
                <span className="font-semibold text-brand-blue">{value}</span>
              </div>
            ))}
          </div>
        </SurfaceCard>

        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Estado de integraciones</h2>
          <div className="mt-6 space-y-4">
            {settingsSnapshot.integrations.map((integration) => (
              <div key={integration.label} className="flex items-center justify-between text-sm text-slate-500">
                <div className="flex items-center gap-3">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${
                      integration.tone === 'green' ? 'bg-emerald-500' : integration.tone === 'amber' ? 'bg-amber-500' : 'bg-blue-500'
                    }`}
                  />
                  {integration.label}
                </div>
                <AppBadge tone={integration.tone === 'green' ? 'green' : integration.tone === 'amber' ? 'amber' : 'blue'}>
                  {integration.status}
                </AppBadge>
              </div>
            ))}
          </div>
          <p className="mt-5 text-sm text-slate-400">Ultima verificacion: Hoy 09:45 AM</p>
        </SurfaceCard>

        <SurfaceCard>
          <h2 className="text-2xl font-semibold text-brand-blue">Destinatarios principales</h2>
          <div className="mt-6 space-y-3">
            {settingsSnapshot.recipients.map((recipient) => (
              <div key={recipient} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-500">
                <span>{recipient}</span>
                <button className="rounded-full bg-red-50 px-2 py-1 text-xs font-semibold text-red-500">x</button>
              </div>
            ))}
          </div>
          <button className="mt-5 w-full rounded-2xl border border-brand-blue/15 bg-white px-4 py-3 text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5">
            + Agregar responsable
          </button>
        </SurfaceCard>
      </div>

      <div className="grid gap-4 xl:grid-cols-[0.72fr_0.72fr]">
        <button className="rounded-2xl bg-brand-blue px-5 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(4,35,84,0.18)] transition hover:-translate-y-0.5">
          Guardar cambios
        </button>
        <button className="rounded-2xl border border-slate-200 bg-white px-5 py-4 text-sm font-semibold text-slate-400 transition hover:bg-slate-50">
          Restablecer valores
        </button>
      </div>
    </div>
  )
}
