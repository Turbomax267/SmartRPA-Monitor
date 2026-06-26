import { useCallback, useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import type { ExecutionListItem, MonitorListItem, PaginationMeta } from '../api/monitor.api'
import { listExecutionsRequest, listRpasRequest } from '../api/monitor.api'
import { AppBadge } from '../components/common/AppBadge'
import { SurfaceCard } from '../components/common/SurfaceCard'

function downloadCsv(filename: string, rows: string[][]) {
  const csv = rows.map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

const filters = {
  status: ['Todos', 'Exitoso', 'Fallido', 'En revision'],
  responsible: ['Todos', 'J. Rodriguez', 'M. Torres', 'A. Garcia', 'R. Silva', 'P. Mendez'],
  errorType: ['Todos', 'Timeout', 'Conexion', 'Datos', 'Credenciales'],
}

export function ExecutionsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [executions, setExecutions] = useState<ExecutionListItem[]>([])
  const [rpaOptions, setRpaOptions] = useState<MonitorListItem[]>([])
  const [search, setSearch] = useState('')
  const [selectedRpaId, setSelectedRpaId] = useState(searchParams.get('rpaId') ?? 'Todos')
  const [status, setStatus] = useState('Todos')
  const [responsible, setResponsible] = useState('Todos')
  const [errorType, setErrorType] = useState('Todos')
  const [page, setPage] = useState(1)
  const [pagination, setPagination] = useState<PaginationMeta>({
    currentPage: 1,
    perPage: 20,
    total: 0,
    lastPage: 1,
    from: 0,
    to: 0,
    hasMorePages: false,
  })

  const formatExecutionDate = (value?: string | null, fallbackDate?: string, fallbackTime?: string) => {
    if (!value) {
      return {
        dateLabel: fallbackDate ?? '-',
        timeLabel: fallbackTime ?? '--:--',
      }
    }

    const date = new Date(value)
    if (Number.isNaN(date.getTime())) {
      return {
        dateLabel: fallbackDate ?? '-',
        timeLabel: fallbackTime ?? '--:--',
      }
    }

    return {
      dateLabel: date.toLocaleDateString([], {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      }),
      timeLabel: date.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      }),
    }
  }

  const loadExecutions = useCallback(async () => {
    const response = await listExecutionsRequest({
      page,
      per_page: 20,
      rpaId: selectedRpaId !== 'Todos' ? selectedRpaId : undefined,
      search: search || undefined,
      status,
      responsible,
      errorType,
    })
    setExecutions(response.data.items)
    setPagination(response.data.pagination)
  }, [errorType, page, responsible, search, selectedRpaId, status])

  useEffect(() => {
    const loadRpas = async () => {
      const response = await listRpasRequest()
      setRpaOptions(response.data)
    }

    void loadRpas()
  }, [])

  useEffect(() => {
    void loadExecutions()
  }, [loadExecutions])

  useEffect(() => {
    const interval = window.setInterval(() => {
      void loadExecutions()
    }, 5000)

    const handleFocus = () => {
      void loadExecutions()
    }

    window.addEventListener('focus', handleFocus)

    return () => {
      window.clearInterval(interval)
      window.removeEventListener('focus', handleFocus)
    }
  }, [loadExecutions])

  useEffect(() => {
    setPage(1)
  }, [search, selectedRpaId, status, responsible, errorType])

  useEffect(() => {
    if (selectedRpaId !== 'Todos') {
      setSearchParams({ rpaId: String(selectedRpaId) })
      return
    }

    setSearchParams({})
  }, [selectedRpaId, setSearchParams])

  const handleExport = () => {
    downloadCsv(
      'ejecuciones-smart-rpa.csv',
      [
        ['Fecha', 'Hora', 'RPA', 'Proceso', 'Estado', 'Duracion', 'Resultado', 'Responsable', 'Tipo Error'],
        ...executions.map((execution) => [
          execution.dateLabel,
          execution.timeLabel,
          execution.rpaName,
          execution.process,
          execution.status,
          execution.durationLabel,
          execution.result,
          execution.responsible,
          execution.errorType,
        ]),
      ],
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-brand-blue">Ejecuciones</h1>
        <p className="mt-2 text-lg text-brand-blue">Historial completo de todas las ejecuciones RPA</p>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_1fr_0.9fr_0.9fr_0.9fr_0.9fr_0.74fr]">
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
        <select
          value={selectedRpaId}
          onChange={(event) => setSelectedRpaId(event.target.value)}
          className="rounded-2xl border border-white/70 bg-white/92 px-4 py-4 text-sm text-brand-blue shadow-soft outline-none"
        >
          <option value="Todos">Todos los RPA</option>
          {rpaOptions.map((rpa) => (
            <option key={String(rpa.id)} value={String(rpa.id)}>
              {String(rpa.name)}
            </option>
          ))}
        </select>
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
        <button onClick={handleExport} className="rounded-2xl bg-emerald-500 px-5 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(34,197,94,0.18)] transition hover:-translate-y-0.5">
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
              {executions.map((execution) => (
                <tr key={execution.id} className="border-b border-slate-100 text-sm text-slate-500 transition hover:bg-slate-50/80">
                  <td className="px-5 py-4">
                    {(() => {
                      const formattedDate = formatExecutionDate(execution.startedAt, execution.dateLabel, execution.timeLabel)

                      return (
                        <>
                          <p>{formattedDate.dateLabel}</p>
                          <p className="text-xs text-slate-400">{formattedDate.timeLabel}</p>
                        </>
                      )
                    })()}
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
          <span>
            Mostrando {pagination.from}-{pagination.to} de {pagination.total} ejecuciones
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={pagination.currentPage <= 1}
              className="rounded-xl border border-slate-200 px-4 py-2 text-brand-blue disabled:cursor-not-allowed disabled:opacity-40"
            >
              Anterior
            </button>
            <button
              type="button"
              onClick={() => setPage((current) => Math.min(pagination.lastPage, current + 1))}
              disabled={pagination.currentPage >= pagination.lastPage}
              className="rounded-xl bg-brand-blue px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-40"
            >
              Siguiente
            </button>
          </div>
        </div>
      </SurfaceCard>
    </div>
  )
}
