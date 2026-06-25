import { ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'

interface BreadcrumbItem {
  label: string
  to?: string
}

export function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  return (
    <div className="mb-3 flex flex-wrap items-center gap-2 text-sm text-slate-400">
      {items.map((item, index) => (
        <span key={`${item.label}-${index}`} className="flex items-center gap-2">
          {item.to ? (
            <Link to={item.to} className="transition hover:text-brand-info">
              {item.label}
            </Link>
          ) : (
            <span className="font-medium text-brand-info">{item.label}</span>
          )}
          {index < items.length - 1 ? <ChevronRight size={14} /> : null}
        </span>
      ))}
    </div>
  )
}
