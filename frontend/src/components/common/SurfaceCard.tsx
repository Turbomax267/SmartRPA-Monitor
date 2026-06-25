import type { ReactNode } from 'react'

export function SurfaceCard({
  children,
  className = '',
  hoverable = false,
}: {
  children: ReactNode
  className?: string
  hoverable?: boolean
}) {
  return (
    <section
      className={`rounded-[28px] border border-white/80 bg-white/92 p-6 shadow-[0_20px_45px_rgba(15,23,42,0.08)] backdrop-blur-sm ${hoverable ? 'transition duration-300 hover:-translate-y-1 hover:shadow-[0_28px_55px_rgba(15,23,42,0.12)]' : ''} ${className}`}
    >
      {children}
    </section>
  )
}
