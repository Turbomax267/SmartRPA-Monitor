import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { listExecutionsRequest } from '../api/monitor.api'
import { AppBadge } from '../components/common/AppBadge'
import { SurfaceCard } from '../components/common/SurfaceCard'

const filters = {
  status: ['Todos', 'Exitoso', 'Fallido', 'En revision'],
  responsible: ['Todos', 'J. Rodriguez', 'M. Torres', 'A. Garcia', 'R. Silva', 'P. Mendez'],
  errorType: ['Todos', 'Timeout', 'Conexion', 'Datos', 'Credenciales'],
}

export function ExecutionsPage() {
  const [executions, setExecutions] = useState<any[]>([])
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('Todos')
  const [responsible, setResponsible] = useState('Todos')
  const [errorType, setErrorType] = useState('Todos')

  useEffect(() => {
    const load = async () => {
      const response = await listExecutionsRequest()
      setExecutions(response.data)
    }

    void load()
  }, [])

  const filteredExecutions = useMemo(() => {
    return executions.filter((item) => {
      const matchesSearch =
        !search ||
        item.rpaName.toLowerCase().includes(search.toLowerCase()) ||
        item.process.toLowerCase().includes(search.toLowerCase())
      const matchesStatus =
        status === 'Todos' ||
        (status === 'Exitoso' && item.status === 'SUCCESS') ||
        (status === 'Fallido' && item.status === 'FAILED') ||
        (status === 'En revision' && item.status === 'REVIEW')
      const matchesResponsible = responsible === 'Todos' || item.responsible === responsible
      const matchesError = errorType === 'Todos' || item.errorType === errorType

      return matchesSearch && matchesStatus && matchesResponsible && matchesError
    })
  }, [errorType, executions, responsible, search, status])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-brand-blue">Ejecuciones</h1>
        <p className="mt-2 text-lg text-brand-blue">Historial completo de todas las ejecuciones RPA</p>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_1fr_0.9fr_0.9fr_0.9fr_0.74fr]">
        <input
          className="rounded-2xl border border-white/70 bg-white/92 px-4 py-4 text-sm text-brand-blue shadow-soft outline-none placeholder:text-slate-400"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Buscar por RPA o proceso"
        />
        <input
          className="rounded-2xl border border-white/70 bg-white/92 px-4 py-4 text-sm text-brand-blue shadow-soft outline-none placeholder:text-slate-400"
          placeholder="Fecha fin"
        />
        {[status, responsible, errorType].map((value, index) => {
          const options = index === 0 ? filters.status : index === 1 ? filters.responsible : filters.errorType
          const setter = index === 0 ? setStatus : index === 1 ? setResponsible : setErrorType

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
        <button className="rounded-2xl bg-emerald-500 px-5 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(34,197,94,0.18)] transition hover:-translate-y-0.5">
          Exportar
        </button>
      </div>

      <SurfaceCard className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left">
            <thead className="bg-brand-blue text-sm text-white">
              <tr>
                {['Fecha', 'RPA', 'Proceso', 'Estado', 'Duracion', 'Resultado', 'Responsable', 'Tipo Error'].map((label) => (
                  <th key={label} className="px-5 py-4">
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredExecutions.map((execution) => (
                <tr key={execution.id} className="border-b border-slate-100 text-sm text-slate-500 transition hover:bg-slate-50/80">
                  <td className="px-5 py-4">
                    <p>{execution.dateLabel}</p>
                    <p className="text-xs text-slate-400">{execution.timeLabel}</p>
                  </td>
                  <td className="px-5 py-4 font-semibold text-brand-blue">
                    <Link to={`/executions/${execution.id}`}>{execution.rpaName}</Link>
                  </td>
                  <td className="px-5 py-4">{execution.process}</td>
                  <td className="px-5 py-4">
                    <AppBadge tone={execution.status === 'SUCCESS' ? 'green' : execution.status === 'FAILED' ? 'red' : 'amber'}>
                      {execution.status === 'SUCCESS' ? 'Exitoso' : execution.status === 'FAILED' ? 'Fallido' : 'En revision'}
                    </AppBadge>
                  </td>
                  <td className="px-5 py-4">{execution.durationLabel}</td>
                  <td className="px-5 py-4">{execution.result}</td>
                  <td className="px-5 py-4">{execution.responsible}</td>
                  <td className={`px-5 py-4 ${execution.errorType !== '-' ? 'text-red-400' : 'text-slate-300'}`}>{execution.errorType}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex items-center justify-between px-5 py-4 text-sm text-slate-400">
          <span>Mostrando 1-{filteredExecutions.length} de 1248 ejecuciones</span>
          <div className="flex gap-2">
            <button className="rounded-xl border border-slate-200 px-4 py-2 text-brand-blue">Anterior</button>
            <button className="rounded-xl bg-brand-blue px-4 py-2 text-white">Siguiente</button>
          </div>
        </div>
      </SurfaceCard>
    </div>
  )
}
