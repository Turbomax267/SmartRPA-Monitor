import { Bot, CalendarRange, ChevronDown, EllipsisVertical, Eye, Hand, Play, Search, SquarePen, Waypoints, X } from 'lucide-react'
import type { ChangeEvent } from 'react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { createJobRequest, listRpasRequest, updateRpaStatusRequest } from '../api/monitor.api'
import { AppBadge } from '../components/common/AppBadge'
import { SurfaceCard } from '../components/common/SurfaceCard'

const processOptions = ['Todos', 'Certificaciones', 'Resultados Academicos', 'Configuracion', 'RRHH', 'Seguridad', 'TI']
const responsibleOptions = ['Todos', 'Equipo Tecnico', 'Maria Rodriguez', 'J. Rodriguez', 'M. Torres', 'A. Garcia']
const statusOptions = ['Todos', 'Activo', 'En revision', 'Inactivo', 'Error']

export function RpasPage() {
  const [rpas, setRpas] = useState<any[]>([])
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('Todos')
  const [process, setProcess] = useState('Todos')
  const [responsible, setResponsible] = useState('Todos')
  const [message, setMessage] = useState<string | null>(null)
  const [openMenuId, setOpenMenuId] = useState<string | number | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const [selectedRpaId, setSelectedRpaId] = useState<string | number | null>(null)
  const [statusModalRpa, setStatusModalRpa] = useState<any | null>(null)
  const [selectedLifecycleStatus, setSelectedLifecycleStatus] = useState<'ACTIVE' | 'INACTIVE' | 'MAINTENANCE'>('INACTIVE')
  const [customImages, setCustomImages] = useState<Record<string, string>>(() => {
    const saved = localStorage.getItem('smart-rpa-card-images')
    return saved ? JSON.parse(saved) : {}
  })

  const getDisplayLifecycleStatus = (rpa: any) => {
    if (rpa.agentStatus !== 'ONLINE') return 'INACTIVE'
    return rpa.lifecycleStatus
  }

  const getLifecycleTone = (status: string) => {
    if (status === 'ACTIVE') return 'green'
    if (status === 'MAINTENANCE' || status === 'UNDER_REVIEW') return 'amber'
    if (status === 'INACTIVE') return 'slate'
    return 'red'
  }

  const getLifecycleLabel = (status: string) => {
    if (status === 'ACTIVE') return 'Activo'
    if (status === 'MAINTENANCE' || status === 'UNDER_REVIEW') return 'En revision'
    if (status === 'INACTIVE') return 'Inactivo'
    return 'Error'
  }

  const loadRpas = async () => {
    const response = await listRpasRequest()
    setRpas(response.data)
  }

  useEffect(() => {
    void loadRpas()
  }, [])

  useEffect(() => {
    localStorage.setItem('smart-rpa-card-images', JSON.stringify(customImages))
  }, [customImages])

  const sendCommand = async (rpa: any, command: 'run' | 'activate' | 'deactivate') => {
    setMessage(null)
    await createJobRequest({
      rpa_id: rpa.id,
      agent_id: rpa.defaultAgentId,
      command,
    })
    setMessage(`Orden enviada: ${command} para ${rpa.name}`)
    await loadRpas()
  }

  const filteredRpas = useMemo(() => {
    return rpas.filter((item) => {
      const matchesQuery =
        !query ||
        item.name.toLowerCase().includes(query.toLowerCase()) ||
        item.processName.toLowerCase().includes(query.toLowerCase())
      const matchesStatus =
        status === 'Todos' ||
        (status === 'Activo' && getDisplayLifecycleStatus(item) === 'ACTIVE') ||
        (status === 'En revision' && ['UNDER_REVIEW', 'MAINTENANCE'].includes(getDisplayLifecycleStatus(item))) ||
        (status === 'Inactivo' && getDisplayLifecycleStatus(item) === 'INACTIVE') ||
        (status === 'Error' && ['ERROR', 'OFFLINE'].includes(item.operationalStatus))
      const matchesProcess = process === 'Todos' || item.processName.includes(process)
      const matchesResponsible = responsible === 'Todos' || item.responsible.includes(responsible)

      return matchesQuery && matchesStatus && matchesProcess && matchesResponsible
    })
  }, [process, query, responsible, rpas, status])

  const handleSelectImage = (rpaId: string | number) => {
    setSelectedRpaId(rpaId)
    fileInputRef.current?.click()
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file || !selectedRpaId) return

    const reader = new FileReader()
    reader.onload = () => {
      setCustomImages((current) => ({
        ...current,
        [String(selectedRpaId)]: String(reader.result),
      }))
    }
    reader.readAsDataURL(file)
    event.target.value = ''
  }

  const handleOpenStatusModal = (rpa: any) => {
    setStatusModalRpa(rpa)
    setSelectedLifecycleStatus((rpa.lifecycleStatus as 'ACTIVE' | 'INACTIVE' | 'MAINTENANCE') ?? 'INACTIVE')
  }

  const handleUpdateLifecycle = async () => {
    if (!statusModalRpa) return

    const response = await updateRpaStatusRequest(statusModalRpa.id, {
      lifecycle_status: selectedLifecycleStatus,
    })

    setRpas((current) =>
      current.map((item) => (item.id === statusModalRpa.id ? response.data : item)),
    )
    setMessage(`Estado actualizado para ${statusModalRpa.name}: ${getLifecycleLabel(selectedLifecycleStatus)}`)
    setStatusModalRpa(null)
  }

  return (
    <div className="space-y-6">
      <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
      <div className="flex items-start justify-between gap-6">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-brand-blue">RPA / Bots</h1>
          <p className="mt-3 text-lg text-brand-blue">Gestion y control de procesos automatizados</p>
        </div>

        <button className="rounded-2xl bg-brand-blue px-8 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(4,35,84,0.18)] transition hover:-translate-y-0.5 hover:bg-[#0b2f6e]">
          + Nuevo RPA
        </button>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.2fr_0.62fr_0.8fr_0.8fr]">
        <label className="flex items-center gap-3 rounded-2xl border border-white/70 bg-white/92 px-4 py-4 shadow-soft">
          <Search size={18} className="text-slate-300" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Buscar RPA..."
            className="w-full bg-transparent text-sm text-brand-blue outline-none placeholder:text-slate-400"
          />
        </label>

        {[status, process, responsible].map((value, index) => {
          const options = index === 0 ? statusOptions : index === 1 ? processOptions : responsibleOptions
          const setter = index === 0 ? setStatus : index === 1 ? setProcess : setResponsible

          return (
            <div key={value + index} className="relative">
              <select
                value={value}
                onChange={(event) => setter(event.target.value)}
                className="w-full appearance-none rounded-2xl border border-white/70 bg-white/92 px-4 py-4 pr-11 text-sm text-brand-blue shadow-soft outline-none transition hover:border-brand-blue/10"
              >
                {options.map((option) => (
                  <option key={option}>{option}</option>
                ))}
              </select>
              <ChevronDown size={18} className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-brand-blue" />
            </div>
          )
        })}
      </div>

      {message && <div className="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</div>}

      <div className="grid gap-5 xl:grid-cols-4">
        {filteredRpas.map((rpa) => (
          <SurfaceCard key={rpa.id} hoverable className="relative overflow-visible p-5">
            <div className="flex items-start justify-between">
              <div className="relative grid h-28 w-28 place-items-center rounded-[2rem] bg-[radial-gradient(circle_at_top,_rgba(230,238,255,1),_rgba(244,246,252,1)_65%)]">
                <Bot size={54} className="text-brand-blue" />
                <div className="absolute -bottom-3 -right-3 grid h-16 w-16 place-items-center overflow-hidden rounded-full border border-white/80 bg-white shadow-soft">
                  {customImages[String(rpa.id)] ? (
                    <img src={customImages[String(rpa.id)]} alt={`Vista ${rpa.name}`} className="h-full w-full object-cover" />
                  ) : (
                    <SquarePen size={20} className="text-brand-info" />
                  )}
                </div>
              </div>
              <div className="relative">
              <button
                type="button"
                onClick={() => setOpenMenuId((current) => (current === rpa.id ? null : rpa.id))}
                className="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-brand-blue"
              >
                <EllipsisVertical size={18} />
              </button>
              {openMenuId === rpa.id && (
                <div className="absolute right-0 top-11 z-20 w-48 rounded-2xl border border-slate-200 bg-white p-2 shadow-[0_18px_34px_rgba(15,23,42,0.12)]">
                  <Link
                    to={`/rpas/${rpa.id}`}
                    className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm text-brand-blue transition hover:bg-slate-50"
                  >
                    <Eye size={16} />
                    Ver detalle
                  </Link>
                  <button
                    type="button"
                    onClick={() => {
                      void sendCommand(rpa, 'run')
                      setOpenMenuId(null)
                    }}
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm text-brand-blue transition hover:bg-slate-50"
                  >
                    <Play size={16} />
                    Ejecutar ahora
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      handleSelectImage(rpa.id)
                      setOpenMenuId(null)
                    }}
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm text-brand-blue transition hover:bg-slate-50"
                  >
                    <SquarePen size={16} />
                    Subir imagen
                  </button>
                </div>
              )}
              </div>
            </div>

            <div className="mt-5">
              <h2 className="text-[1.6rem] font-bold leading-tight text-brand-blue">{rpa.name}</h2>
              <p className="mt-2 text-sm text-slate-400">Proceso: {rpa.processName}</p>
              <p className="mt-1 text-sm text-slate-400">Responsable: {rpa.responsible}</p>
            </div>

            <div className="mt-4">
              <AppBadge
                tone={getLifecycleTone(getDisplayLifecycleStatus(rpa))}
                >
                  {getLifecycleLabel(getDisplayLifecycleStatus(rpa))}
              </AppBadge>
              <div className="mt-2">
                <AppBadge tone={rpa.agentStatus === 'ONLINE' ? 'green' : 'slate'}>
                  {rpa.agentStatus === 'ONLINE' ? 'Agente online' : 'Agente offline'}
                </AppBadge>
              </div>
            </div>

            <div className="mt-5 space-y-3 text-sm text-slate-500">
              <div className="flex items-center gap-2">
                <CalendarRange size={16} className="text-slate-300" />
                Ultima ejecucion: {rpa.lastExecutionLabel}
              </div>
              <div className="flex items-center gap-2">
                <SquarePen size={16} className="text-slate-300" />
                Script: {rpa.scriptName}
              </div>
              <div className="flex items-center gap-2">
                <Waypoints size={16} className="text-slate-300" />
                Modo: {rpa.executionMode}
              </div>
            </div>

            <div className="mt-6 grid grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => handleOpenStatusModal(rpa)}
                className="rounded-2xl border border-slate-200 py-3 text-brand-blue transition hover:border-brand-blue/20 hover:bg-brand-blue/5"
              >
                <Hand size={18} className="mx-auto" />
              </button>
              <Link
                to={`/rpas/${rpa.id}`}
                className="rounded-2xl border border-slate-200 py-3 text-center text-sm font-semibold text-brand-info transition hover:border-brand-info/20 hover:bg-brand-info/5"
              >
                Ver
              </Link>
              <button
                type="button"
                onClick={() => void sendCommand(rpa, 'run')}
                className="rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-brand-blue transition hover:border-brand-blue/20 hover:bg-brand-blue/5"
              >
                <Play size={18} className="mx-auto" />
              </button>
            </div>
          </SurfaceCard>
        ))}
      </div>

      {statusModalRpa && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 px-4 backdrop-blur-sm">
          <div className="w-full max-w-xl rounded-[32px] bg-white p-7 shadow-[0_32px_80px_rgba(15,23,42,0.22)]">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-2xl font-bold text-brand-blue">Cambiar estado del RPA</h3>
                <p className="mt-2 text-sm text-slate-400">{statusModalRpa.name}</p>
              </div>
              <button
                type="button"
                onClick={() => setStatusModalRpa(null)}
                className="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-brand-blue"
              >
                <X size={18} />
              </button>
            </div>

            <div className="mt-6 grid gap-3">
              {[
                { value: 'ACTIVE', label: 'Activo', helper: 'Visible como habilitado cuando el agente este online.' },
                { value: 'INACTIVE', label: 'Inactivo', helper: 'Bloquea su uso operativo desde el monitor.' },
                { value: 'MAINTENANCE', label: 'En revision', helper: 'Ideal para mantenimiento o validacion.' },
              ].map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setSelectedLifecycleStatus(option.value as 'ACTIVE' | 'INACTIVE' | 'MAINTENANCE')}
                  className={`rounded-2xl border px-4 py-4 text-left transition ${
                    selectedLifecycleStatus === option.value
                      ? 'border-brand-blue bg-brand-blue/5 shadow-soft'
                      : 'border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-semibold text-brand-blue">{option.label}</p>
                      <p className="mt-1 text-sm text-slate-400">{option.helper}</p>
                    </div>
                    <AppBadge tone={getLifecycleTone(option.value)}>{option.label}</AppBadge>
                  </div>
                </button>
              ))}
            </div>

            <div className="mt-7 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setStatusModalRpa(null)}
                className="rounded-2xl border border-slate-200 px-5 py-3 text-sm font-semibold text-brand-blue transition hover:bg-slate-50"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={() => void handleUpdateLifecycle()}
                className="rounded-2xl bg-brand-blue px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#0b2f6e]"
              >
                Guardar estado
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
