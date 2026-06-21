interface PagePlaceholderProps {
  title: string
  description: string
}

export function PagePlaceholder({ title, description }: PagePlaceholderProps) {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-3xl font-bold text-brand-blue">{title}</h1>
        <p className="mt-2 text-sm text-slate-500">{description}</p>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-soft">
        <div className="flex min-h-72 items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50">
          <div className="text-center">
            <p className="text-xl font-semibold text-brand-blue">Módulo en construcción</p>
            <p className="mt-2 text-sm text-slate-500">
              La estructura ya está lista para continuar esta siguiente fase.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
