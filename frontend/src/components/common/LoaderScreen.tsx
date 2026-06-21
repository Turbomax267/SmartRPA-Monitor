export function LoaderScreen({ message = 'Cargando...' }: { message?: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100">
      <div className="rounded-2xl bg-white px-8 py-6 shadow-soft">
        <div className="flex items-center gap-3">
          <div className="h-3 w-3 animate-pulse rounded-full bg-brand-yellow" />
          <span className="text-sm font-medium text-slate-600">{message}</span>
        </div>
      </div>
    </div>
  )
}
