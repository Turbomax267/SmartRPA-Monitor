export function formatNumber(value: number) {
  return new Intl.NumberFormat('es-PE').format(value)
}

export function formatPercent(value: number) {
  return `${value.toFixed(1)}%`
}

export function formatDuration(milliseconds: number) {
  if (milliseconds < 60000) {
    return `${Math.round(milliseconds / 1000)} seg`
  }

  const minutes = milliseconds / 60000

  return `${minutes.toFixed(1)} min`
}

export function formatDateLabel(value: string | null) {
  if (!value) {
    return 'Sin fecha'
  }

  return new Intl.DateTimeFormat('es-PE', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
  }).format(new Date(value))
}
