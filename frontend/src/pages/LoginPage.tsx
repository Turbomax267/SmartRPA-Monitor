import { Eye, EyeOff, LockKeyhole, Mail } from 'lucide-react'
import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import logo from '../assets/branding/logo.png'
import { AnimatedLoginBackground } from '../components/layout/AnimatedLoginBackground'
import { useAuth } from '../hooks/useAuth'

export function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [remember, setRemember] = useState(true)
  const [email, setEmail] = useState('admin@smartrpa.local')
  const [password, setPassword] = useState('SmartRPA123*')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({})

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsSubmitting(true)
    setErrorMessage(null)
    setFieldErrors({})

    try {
      await login({ email, password }, { remember })
      navigate('/dashboard', { replace: true })
    } catch (error: unknown) {
      const message =
        typeof error === 'object' &&
        error !== null &&
        'message' in error &&
        typeof error.message === 'string' &&
        error.message === 'Network Error'
          ? 'No se pudo conectar con la API. Verifica la URL del backend, CORS y que el servicio este arriba.'
          : error instanceof Error
            ? error.message
            : 'No se pudo iniciar sesion.'
      const responseErrors =
        typeof error === 'object' &&
        error !== null &&
        'response' in error &&
        typeof error.response === 'object' &&
        error.response !== null &&
        'data' in error.response &&
        typeof error.response.data === 'object' &&
        error.response.data !== null &&
        'errors' in error.response.data &&
        typeof error.response.data.errors === 'object'
          ? (error.response.data.errors as Record<string, string[]>)
          : {}

      setFieldErrors(responseErrors)
      setErrorMessage(responseErrors.email?.[0] ?? message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.05fr_1fr]">
      <section className="relative hidden overflow-hidden bg-brand-blue px-10 py-12 text-white lg:flex lg:flex-col lg:justify-center">
        <AnimatedLoginBackground />

        <div className="animate-soft-reveal relative z-10 mx-auto flex w-full max-w-3xl flex-col items-center text-center">
          <div className="mb-10 h-1 w-12 rounded-full bg-brand-yellow" />
          <img src={logo} alt="SmartRPA Monitor" className="mb-6 h-80 w-auto object-contain xl:h-[24rem]" />
        </div>
      </section>

      <section className="flex items-center justify-center bg-slate-100 px-5 py-10">
        <div className="animate-soft-reveal w-full max-w-md rounded-[2rem] border-t-4 border-brand-yellow bg-white p-8 shadow-[0_28px_60px_rgba(4,35,84,0.08)] [animation-delay:140ms]">
          <div className="mb-8 lg:hidden">
            <img src={logo} alt="SmartRPA Monitor" className="h-36 w-auto object-contain" />
          </div>

          <h2 className="text-4xl font-bold text-brand-blue">Bienvenido</h2>
          <p className="mt-2 text-sm text-slate-400">Ingresa tus credenciales de acceso</p>

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="mb-2 block text-sm font-semibold text-brand-blue">Correo electronico</label>
              <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4">
                <Mail size={18} className="text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="w-full bg-transparent py-4 text-sm text-brand-blue outline-none placeholder:text-slate-400"
                  placeholder="usuario@empresa.com"
                />
              </div>
              {fieldErrors.email?.[0] && <p className="mt-2 text-xs text-red-500">{fieldErrors.email[0]}</p>}
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-brand-blue">Contraseña</label>
              <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4">
                <LockKeyhole size={18} className="text-slate-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="w-full bg-transparent py-4 text-sm text-brand-blue outline-none placeholder:text-slate-400"
                  placeholder="************"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((current) => !current)}
                  className="text-slate-400 transition hover:text-brand-blue"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {fieldErrors.password?.[0] && (
                <p className="mt-2 text-xs text-red-500">{fieldErrors.password[0]}</p>
              )}
            </div>

            <div className="flex items-center justify-between gap-4 text-sm">
              <label className="flex items-center gap-2 text-slate-500">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(event) => setRemember(event.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 text-brand-blue focus:ring-brand-yellow"
                />
                Recordarme
              </label>
              <span className="text-brand-info">Olvidaste tu contraseña?</span>
            </div>

            {errorMessage && (
              <div className="rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-600">
                {errorMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="flex w-full items-center justify-center rounded-2xl bg-brand-blue px-5 py-4 text-sm font-semibold text-white transition hover:bg-[#0A2D67] disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isSubmitting ? 'Validando acceso...' : 'Iniciar sesion'}
            </button>

            <div className="border-t border-slate-100 pt-5 text-center text-xs text-slate-400">
              Acceso restringido - Solo usuarios autorizados - 2025 SmartRPA Monitor
            </div>
          </form>
        </div>
      </section>
    </div>
  )
}
