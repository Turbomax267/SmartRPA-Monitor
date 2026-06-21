export function AnimatedLoginBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <div className="absolute -left-24 -top-16 h-72 w-72 rounded-full bg-white/5 blur-sm" />
      <div className="absolute bottom-10 right-12 h-56 w-56 rounded-full bg-white/5 blur-sm" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(250,214,52,0.14),transparent_30%),radial-gradient(circle_at_bottom_right,rgba(59,130,246,0.12),transparent_35%),linear-gradient(135deg,rgba(255,255,255,0.03),transparent_55%)]" />
      <div className="pattern-grid absolute inset-0 opacity-25" />
      <div className="pattern-orbits absolute inset-0 opacity-55" />
      <div className="pattern-beams absolute inset-0 opacity-40" />
      <div className="pattern-wave absolute inset-x-0 bottom-0 h-48 opacity-40" />

      {Array.from({ length: 18 }).map((_, index) => (
        <span
          key={index}
          className="particle animate-float-particle"
          style={{
            left: `${8 + index * 5.2}%`,
            top: `${10 + (index % 5) * 18}%`,
            ['--particle-x1' as string]: `${6 + (index % 4) * 5}px`,
            ['--particle-y1' as string]: `${-8 - (index % 3) * 6}px`,
            ['--particle-x2' as string]: `${18 + (index % 5) * 4}px`,
            ['--particle-y2' as string]: `${-18 - (index % 4) * 7}px`,
            ['--particle-x3' as string]: `${10 + (index % 6) * 3}px`,
            ['--particle-y3' as string]: `${-28 - (index % 5) * 6}px`,
            ['--particle-x4' as string]: `${-4 - (index % 3) * 4}px`,
            ['--particle-y4' as string]: `${-14 - (index % 4) * 5}px`,
            animationDelay: `${index * 0.45}s`,
            animationDuration: `${16 + (index % 4) * 3}s`,
          }}
        />
      ))}

      {Array.from({ length: 5 }).map((_, index) => (
        <span
          key={`ring-${index}`}
          className="orbital-ring animate-rotate-drift"
          style={{
            width: `${180 + index * 90}px`,
            height: `${180 + index * 90}px`,
            left: `${-10 + index * 14}%`,
            top: `${-6 + index * 13}%`,
            animationDuration: `${18 + index * 5}s`,
            animationDelay: `${index * 0.8}s`,
          }}
        />
      ))}
    </div>
  )
}
