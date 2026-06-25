import { Eye, EyeOff } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { AppBadge } from '../components/common/AppBadge'
import { SurfaceCard } from '../components/common/SurfaceCard'
import { getRoleCard, roleCards } from '../mocks/monitorData'

const rolePermissionSummary = {
  ADMIN: ['Consultar ejecuciones', 'Revisar incidentes', 'Acceder a metricas', 'Gestionar usuarios', 'Configurar sistema'],
  TECH: ['Consultar ejecuciones', 'Revisar incidentes', 'Acceder a metricas', 'Gestionar usuarios', 'Configurar sistema'],
  MANAGER: ['Consultar ejecuciones', 'Revisar incidentes', 'Acceder a metricas', 'Gestionar usuarios', 'Configurar sistema'],
}

export function UserFormPage() {
  const [selectedRole, setSelectedRole] = useState<'ADMIN' | 'TECH' | 'MANAGER'>('ADMIN')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [password, setPassword] = useState('')

  const passwordStrength = useMemo(() => {
    if (password.length >= 12) return 'Muy fuerte'
    if (password.length >= 9) return 'Fuerte'
    if (password.length >= 6) return 'Media'
    return 'Debil'
  }, [password])

  const role = getRoleCard(selectedRole)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-brand-blue">Crear Usuario</h1>
        <p className="mt-2 text-lg text-brand-blue">Alta de nuevos usuarios y asignacion de roles</p>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.5fr_0.95fr]">
        <div className="space-y-5">
          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Informacion del Usuario</h2>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {[
                ['Nombres *', 'Ej. Carlos Alberto'],
                ['Apellidos *', 'Ej. Mendoza Garcia'],
                ['Correo electronico *', 'Ej. carlos.mendoza@empresa.com'],
                ['Nombre de usuario *', 'Ej. carlos.mendoza'],
                ['Area *', 'Selecciona un area'],
                ['Cargo *', 'Ej. Analista de Procesos'],
                ['Telefono (opcional)', 'Ej. +52 55 1234 5678'],
              ].map(([label, placeholder], index) => (
                <div key={label} className={index === 2 ? 'md:col-span-2' : ''}>
                  <label className="mb-2 block text-sm font-semibold text-brand-blue">{label}</label>
                  {label.includes('Area') || label.includes('Cargo') ? (
                    <select className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-brand-blue outline-none">
                      <option>{placeholder}</option>
                    </select>
                  ) : (
                    <input
                      placeholder={placeholder}
                      className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-brand-blue outline-none placeholder:text-slate-400"
                    />
                  )}
                </div>
              ))}

              <div>
                <label className="mb-2 block text-sm font-semibold text-brand-blue">Contrasena *</label>
                <div className="flex items-center rounded-2xl border border-slate-200 bg-slate-50 px-4">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Minimo 8 caracteres"
                    className="w-full bg-transparent py-4 text-sm text-brand-blue outline-none placeholder:text-slate-400"
                  />
                  <button type="button" onClick={() => setShowPassword((current) => !current)} className="text-slate-400">
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-brand-blue">Confirmar contrasena *</label>
                <div className="flex items-center rounded-2xl border border-slate-200 bg-slate-50 px-4">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="Repite la contrasena"
                    className="w-full bg-transparent py-4 text-sm text-brand-blue outline-none placeholder:text-slate-400"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword((current) => !current)}
                    className="text-slate-400"
                  >
                    {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
              <span className="font-semibold text-brand-blue">Fortaleza de la contrasena:</span>
              <AppBadge tone="red">Debil</AppBadge>
              <AppBadge tone="amber">Media</AppBadge>
              <AppBadge tone="green">Fuerte</AppBadge>
              <AppBadge tone="green">{passwordStrength}</AppBadge>
            </div>
          </SurfaceCard>

          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Estado y acceso</h2>
            <div className="mt-6 space-y-4 text-sm text-slate-500">
              <div className="grid grid-cols-[1fr_0.8fr_0.8fr] items-center gap-3 rounded-2xl bg-slate-50 px-4 py-3">
                <span className="font-semibold text-brand-blue">Estado del usuario *</span>
                <button className="rounded-2xl bg-emerald-50 px-4 py-2 font-semibold text-emerald-600">Activo</button>
                <button className="rounded-2xl bg-white px-4 py-2 font-semibold text-slate-400">Inactivo</button>
              </div>
              {[
                'Enviar credenciales por correo',
                'Requerir cambio de contrasena en primer acceso',
                'Acceso temporal',
              ].map((label, index) => (
                <div key={label} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                  <span>{label}</span>
                  <button
                    className={`h-7 w-14 rounded-full transition ${index < 2 ? 'bg-emerald-500' : 'bg-slate-300'}`}
                  >
                    <span
                      className={`block h-6 w-6 rounded-full bg-white shadow transition ${index < 2 ? 'translate-x-7' : 'translate-x-0.5'}`}
                    />
                  </button>
                </div>
              ))}
            </div>
          </SurfaceCard>

          <div className="grid gap-4 xl:grid-cols-3">
            <button className="rounded-2xl bg-brand-blue px-5 py-4 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(4,35,84,0.18)] transition hover:-translate-y-0.5">
              Guardar Usuario
            </button>
            <Link
              to="/users"
              className="rounded-2xl border border-slate-200 bg-white px-5 py-4 text-center text-sm font-semibold text-brand-blue transition hover:bg-brand-blue/5"
            >
              Cancelar
            </Link>
            <button className="rounded-2xl border border-brand-info/25 bg-white px-5 py-4 text-sm font-semibold text-brand-info transition hover:bg-brand-info/5">
              Limpiar formulario
            </button>
          </div>
        </div>

        <div className="space-y-5">
          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Rol asignado</h2>
            <p className="mt-2 text-sm text-slate-400">Selecciona el rol que tendra este usuario en el sistema</p>
            <div className="mt-6 space-y-3">
              {roleCards.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setSelectedRole(item.id)}
                  className={`grid w-full grid-cols-[56px_1fr_24px] items-center gap-4 rounded-[24px] border px-4 py-4 text-left transition ${
                    selectedRole === item.id ? 'border-blue-400 bg-blue-50/60 shadow-soft' : 'border-slate-200 bg-white'
                  }`}
                >
                  <div
                    className={`flex h-14 w-14 items-center justify-center rounded-full font-bold ${
                      item.accent === 'navy'
                        ? 'bg-brand-blue/10 text-brand-blue'
                        : item.accent === 'blue'
                          ? 'bg-blue-50 text-blue-600'
                          : 'bg-emerald-50 text-emerald-600'
                    }`}
                  >
                    {item.short}
                  </div>
                  <div>
                    <p className="text-xl font-semibold text-brand-blue">{item.title}</p>
                    <p className="mt-1 text-sm text-slate-400">{item.permissions[0]}</p>
                  </div>
                  <span className={`h-6 w-6 rounded-full border-2 ${selectedRole === item.id ? 'border-blue-500 bg-blue-500' : 'border-slate-300'}`} />
                </button>
              ))}
            </div>
          </SurfaceCard>

          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Permisos principales</h2>
            <p className="mt-2 text-sm text-slate-400">Permisos que tendra el usuario segun el rol seleccionado</p>
            <div className="mt-6 space-y-4">
              {rolePermissionSummary[selectedRole].map((permission, index) => (
                <div key={permission} className="flex items-center justify-between">
                  <span className="text-sm text-slate-500">{permission}</span>
                  <AppBadge tone={index < 3 || selectedRole === 'ADMIN' ? 'green' : 'slate'}>
                    {index < 3 || selectedRole === 'ADMIN' ? 'Permitido' : 'No permitido'}
                  </AppBadge>
                </div>
              ))}
            </div>
          </SurfaceCard>

          <SurfaceCard>
            <h2 className="text-2xl font-semibold text-brand-blue">Resumen de creacion</h2>
            <div className="mt-6 space-y-4 text-sm text-slate-500">
              <div className="flex justify-between">
                <span>Rol seleccionado</span>
                <AppBadge tone={role.accent === 'navy' ? 'navy' : role.accent === 'blue' ? 'blue' : 'green'}>
                  {role.title}
                </AppBadge>
              </div>
              <div className="flex justify-between">
                <span>Estado del usuario</span>
                <AppBadge tone="green">Activo</AppBadge>
              </div>
              <div className="flex justify-between">
                <span>Area asignada</span>
                <AppBadge tone="slate">No seleccionada</AppBadge>
              </div>
              <div className="flex justify-between">
                <span>Metodo de notificacion</span>
                <AppBadge tone="blue">Por correo electronico</AppBadge>
              </div>
            </div>
          </SurfaceCard>
        </div>
      </div>
    </div>
  )
}
