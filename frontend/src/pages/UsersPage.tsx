import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { usersRequest } from '../api/monitor.api'
import { AppBadge } from '../components/common/AppBadge'
import { SurfaceCard } from '../components/common/SurfaceCard'
import { getRoleCard, roleCards } from '../mocks/monitorData'

export function UsersPage() {
  const [monitorUsers, setMonitorUsers] = useState<any[]>([])

  useEffect(() => {
    const load = async () => {
      const response = await usersRequest()
      setMonitorUsers(response.data.users)
    }

    void load()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-6">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-brand-blue">Usuarios y Roles</h1>
          <p className="mt-2 text-lg text-brand-blue">Gestion de accesos y permisos del sistema</p>
        </div>

        <Link
          to="/users/new"
          className="rounded-2xl bg-brand-blue px-6 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(4,35,84,0.18)] transition hover:-translate-y-0.5"
        >
          + Nuevo Usuario
        </Link>
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        {roleCards.map((role) => (
          <SurfaceCard key={role.id}>
            <div className={`mb-4 h-1 w-full rounded-full ${role.accent === 'navy' ? 'bg-brand-blue' : role.accent === 'blue' ? 'bg-blue-500' : 'bg-emerald-500'}`} />
            <div className="flex items-start gap-4">
              <div className={`flex h-12 w-12 items-center justify-center rounded-full font-bold ${role.accent === 'navy' ? 'bg-brand-blue/10 text-brand-blue' : role.accent === 'blue' ? 'bg-blue-50 text-blue-600' : 'bg-emerald-50 text-emerald-600'}`}>
                {role.short}
              </div>
              <div>
                <h2 className="text-2xl font-semibold text-brand-blue">{role.title}</h2>
                <p className="text-sm text-slate-400">{role.description}</p>
              </div>
            </div>
            <ul className="mt-5 space-y-3 text-sm text-slate-500">
              {role.permissions.map((permission) => (
                <li key={permission} className="flex items-start gap-3">
                  <span className="mt-2 h-2 w-2 rounded-full bg-brand-blue" />
                  <span>{permission}</span>
                </li>
              ))}
            </ul>
          </SurfaceCard>
        ))}
      </div>

      <SurfaceCard className="overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left">
            <thead className="bg-brand-blue text-sm text-white">
              <tr>
                {['Usuario', 'Nombre', 'Rol', 'Area', 'Estado', 'Ultimo Acceso', 'Acciones'].map((label) => (
                  <th key={label} className="px-4 py-4">
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {monitorUsers.map((user) => {
                const role = getRoleCard(user.role)

                return (
                  <tr key={user.id} className="border-b border-slate-100 text-sm text-slate-500 transition hover:bg-slate-50/80">
                    <td className="px-4 py-4 font-semibold text-brand-blue">{user.email}</td>
                    <td className="px-4 py-4">{user.name}</td>
                    <td className="px-4 py-4">
                      <AppBadge tone={role.accent === 'navy' ? 'navy' : role.accent === 'blue' ? 'blue' : 'green'}>
                        {role.title}
                      </AppBadge>
                    </td>
                    <td className="px-4 py-4">{user.area}</td>
                    <td className="px-4 py-4">
                      <AppBadge tone={user.status === 'ACTIVE' ? 'green' : 'slate'}>
                        {user.status === 'ACTIVE' ? 'Activo' : 'Inactivo'}
                      </AppBadge>
                    </td>
                    <td className="px-4 py-4">{user.lastAccess}</td>
                    <td className="px-4 py-4">
                      <div className="flex gap-2">
                        <Link to="/users/new" className="rounded-xl bg-blue-50 px-3 py-2 text-xs font-semibold text-blue-600">
                          Ed.
                        </Link>
                        <button className="rounded-xl bg-red-50 px-3 py-2 text-xs font-semibold text-red-500">Del.</button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </SurfaceCard>
    </div>
  )
}
