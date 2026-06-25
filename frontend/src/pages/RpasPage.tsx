import { Bot, CalendarRange, EllipsisVertical, Play, Search, SquarePen, Waypoints } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { AppBadge } from '../components/common/AppBadge'
import { SurfaceCard } from '../components/common/SurfaceCard'
import { rpaCatalog } from '../mocks/monitorData'

const processOptions = ['Todos', 'Certificaciones', 'Resultados Academicos', 'Configuracion', 'RRHH', 'Seguridad', 'TI']
const responsibleOptions = ['Todos', 'Equipo Tecnico', 'Maria Rodriguez', 'J. Rodriguez', 'M. Torres', 'A. Garcia']
const statusOptions = ['Todos', 'Activo', 'En revision', 'Inactivo', 'Error']

export function RpasPage() {
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('Todos')
  const [process, setProcess] = useState('Todos')
  const [responsible, setResponsible] = useState('Todos')

  const filteredRpas = useMemo(() => {
    return rpaCatalog.filter((item) => {
      const matchesQuery =
        !query ||
        item.name.toLowerCase().includes(query.toLowerCase()) ||
        item.processName.toLowerCase().includes(query.toLowerCase())
      const matchesStatus =
        status === 'Todos' ||
        (status === 'Activo' && item.lifecycleStatus === 'ACTIVE') ||
        (status === 'En revision' && item.lifecycleStatus === 'UNDER_REVIEW') ||
        (status === 'Inactivo' && item.lifecycleStatus === 'INACTIVE') ||
        (status === 'Error' && item.lifecycleStatus === 'ERROR')
      const matchesProcess = process === 'Todos' || item.processName.includes(process)
      const matchesResponsible = responsible === 'Todos' || item.responsible.includes(responsible)

      return matchesQuery && matchesStatus && matchesProcess && matchesResponsible
    })
  }, [process, query, responsible, status])

  return (
    <div className="space-y-6">
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
            <select
              key={value + index}
              value={value}
              onChange={(event) => setter(event.target.value)}
              className="rounded-2xl border border-white/70 bg-white/92 px-4 py-4 text-sm text-brand-blue shadow-soft outline-none"
            >
              {options.map((option) => (
                <option key={option}>{option}</option>
              ))}
            </select>
          )
        })}
      </div>

      <div className="grid gap-5 xl:grid-cols-4">
        {filteredRpas.map((rpa) => (
          <SurfaceCard key={rpa.id} hoverable className="p-5">
            <div className="flex items-start justify-between">
              <div className="grid h-28 w-28 place-items-center rounded-[2rem] bg-[radial-gradient(circle_at_top,_rgba(230,238,255,1),_rgba(244,246,252,1)_65%)]">
                <Bot size={54} className="text-brand-blue" />
              </div>
              <button className="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-brand-blue">
                <EllipsisVertical size={18} />
              </button>
            </div>

            <div className="mt-5">
              <h2 className="text-[1.6rem] font-bold leading-tight text-brand-blue">{rpa.name}</h2>
              <p className="mt-2 text-sm text-slate-400">Proceso: {rpa.processName}</p>
              <p className="mt-1 text-sm text-slate-400">Responsable: {rpa.responsible}</p>
            </div>

            <div className="mt-4">
              <AppBadge
                tone={
                  rpa.lifecycleStatus === 'ACTIVE'
                    ? 'green'
                    : rpa.lifecycleStatus === 'UNDER_REVIEW'
                      ? 'amber'
                      : rpa.lifecycleStatus === 'INACTIVE'
                        ? 'slate'
                        : 'red'
                }
              >
                {rpa.lifecycleStatus === 'ACTIVE'
                  ? 'Activo'
                  : rpa.lifecycleStatus === 'UNDER_REVIEW'
                    ? 'En revision'
                    : rpa.lifecycleStatus === 'INACTIVE'
                      ? 'Inactivo'
                      : 'Error'}
              </AppBadge>
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
              <button className="rounded-2xl border border-slate-200 py-3 text-brand-blue transition hover:border-brand-blue/20 hover:bg-brand-blue/5">
                <Play size={18} className="mx-auto" />
              </button>
              <Link
                to={`/rpas/${rpa.id}`}
                className="rounded-2xl border border-slate-200 py-3 text-center text-sm font-semibold text-brand-info transition hover:border-brand-info/20 hover:bg-brand-info/5"
              >
                Ver
              </Link>
              <button className="rounded-2xl border border-slate-200 py-3 text-sm font-semibold text-brand-blue transition hover:border-brand-blue/20 hover:bg-brand-blue/5">
                Editar
              </button>
            </div>
          </SurfaceCard>
        ))}
      </div>
    </div>
  )
}
