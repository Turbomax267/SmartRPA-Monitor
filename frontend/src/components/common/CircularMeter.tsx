export function CircularMeter({
  value,
  label,
  sublabel,
  tone = '#22c55e',
  size = 132,
}: {
  value: number
  label: string
  sublabel?: string
  tone?: string
  size?: number
}) {
  const ring = `conic-gradient(${tone} 0 ${value}%, rgba(226,232,240,0.7) ${value}% 100%)`

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className="grid place-items-center rounded-full"
        style={{
          width: size,
          height: size,
          background: ring,
        }}
      >
        <div
          className="grid place-items-center rounded-full bg-white text-center shadow-inner"
          style={{ width: size - 28, height: size - 28 }}
        >
          <div>
            <p className="text-4xl font-bold text-brand-blue">{value}%</p>
            <p className="mt-1 text-xs font-medium text-slate-400">{label}</p>
          </div>
        </div>
      </div>
      {sublabel ? <p className="text-lg font-semibold text-emerald-500">{sublabel}</p> : null}
    </div>
  )
}
