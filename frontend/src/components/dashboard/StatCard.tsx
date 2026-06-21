import type { ReactNode } from 'react'

interface StatCardProps {
  title: string
  value: string
  subtitle: string
  accent: string
  icon: ReactNode
}

export function StatCard({ title, value, subtitle, accent, icon }: StatCardProps) {
  return (
    <div className="rounded-3xl bg-white p-5 shadow-soft">
      <div className={`mb-4 h-1 rounded-full ${accent}`} />
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-4xl font-bold text-brand-blue">{value}</p>
          <h3 className="mt-3 text-sm font-semibold text-brand-blue">{title}</h3>
          <p className="mt-1 text-xs text-slate-400">{subtitle}</p>
        </div>
        <div className="rounded-2xl bg-slate-100 p-3 text-slate-400">{icon}</div>
      </div>
    </div>
  )
}
