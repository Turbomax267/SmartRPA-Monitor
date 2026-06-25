import type { ReactNode } from 'react'

type Tone = 'navy' | 'blue' | 'green' | 'amber' | 'red' | 'purple' | 'slate' | 'teal'
type Variant = 'soft' | 'solid' | 'outline'

const toneClasses: Record<Tone, Record<Variant, string>> = {
  navy: {
    soft: 'bg-brand-blue/8 text-brand-blue border border-brand-blue/10',
    solid: 'bg-brand-blue text-white border border-brand-blue',
    outline: 'bg-white text-brand-blue border border-brand-blue/20',
  },
  blue: {
    soft: 'bg-blue-50 text-blue-600 border border-blue-100',
    solid: 'bg-blue-500 text-white border border-blue-500',
    outline: 'bg-white text-blue-600 border border-blue-200',
  },
  green: {
    soft: 'bg-emerald-50 text-emerald-600 border border-emerald-100',
    solid: 'bg-emerald-500 text-white border border-emerald-500',
    outline: 'bg-white text-emerald-600 border border-emerald-200',
  },
  amber: {
    soft: 'bg-amber-50 text-amber-600 border border-amber-100',
    solid: 'bg-amber-500 text-white border border-amber-500',
    outline: 'bg-white text-amber-600 border border-amber-200',
  },
  red: {
    soft: 'bg-red-50 text-red-500 border border-red-100',
    solid: 'bg-red-500 text-white border border-red-500',
    outline: 'bg-white text-red-500 border border-red-200',
  },
  purple: {
    soft: 'bg-violet-50 text-violet-600 border border-violet-100',
    solid: 'bg-violet-500 text-white border border-violet-500',
    outline: 'bg-white text-violet-600 border border-violet-200',
  },
  slate: {
    soft: 'bg-slate-100 text-slate-500 border border-slate-200',
    solid: 'bg-slate-500 text-white border border-slate-500',
    outline: 'bg-white text-slate-500 border border-slate-200',
  },
  teal: {
    soft: 'bg-cyan-50 text-cyan-700 border border-cyan-100',
    solid: 'bg-cyan-600 text-white border border-cyan-600',
    outline: 'bg-white text-cyan-700 border border-cyan-200',
  },
}

export function AppBadge({
  children,
  tone = 'navy',
  variant = 'soft',
  icon,
  className = '',
}: {
  children: ReactNode
  tone?: Tone
  variant?: Variant
  icon?: ReactNode
  className?: string
}) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold tracking-[0.01em] ${toneClasses[tone][variant]} ${className}`}
    >
      {icon}
      {children}
    </span>
  )
}
