interface FlowMeterProps {
  /** 瞬时流速 L/min */
  flowRate: number
  /** 最大量程 L/min */
  maxRange?: number
  size?: number
}

export default function FlowMeter({
  flowRate,
  maxRange = 20,
  size = 100,
}: FlowMeterProps) {
  const cx = size / 2
  const cy = size / 2 + 8
  const radius = size / 2 - 12

  // 指针角度: -90° (0) 到 +90° (maxRange)
  const clampRate = Math.max(0, Math.min(flowRate, maxRange))
  const angle = -90 + (clampRate / maxRange) * 180

  // 刻度线
  const ticks = []
  for (let i = 0; i <= 10; i++) {
    const tickAngle = (-90 + (i / 10) * 180) * (Math.PI / 180)
    const innerR = radius - 8
    const outerR = i % 5 === 0 ? radius - 2 : radius - 5
    ticks.push(
      <line
        key={i}
        x1={cx + innerR * Math.cos(tickAngle)}
        y1={cy + innerR * Math.sin(tickAngle)}
        x2={cx + outerR * Math.cos(tickAngle)}
        y2={cy + outerR * Math.sin(tickAngle)}
        stroke="#94a3b8"
        strokeWidth={i % 5 === 0 ? 1.5 : 0.8}
      />
    )
  }

  return (
    <svg width={size} height={size + 16} viewBox={`0 0 ${size} ${size + 16}`}>
      {/* 圆弧背景 */}
      <path
        d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
        fill="none"
        stroke="#334155"
        strokeWidth={2}
      />

      {/* 刻度线 */}
      {ticks}

      {/* 指针 */}
      <line
        x1={cx}
        y1={cy}
        x2={cx + (radius - 14) * Math.cos(angle * Math.PI / 180)}
        y2={cy + (radius - 14) * Math.sin(angle * Math.PI / 180)}
        stroke="#f59e0b"
        strokeWidth={2}
        strokeLinecap="round"
      >
        <animateTransform
          attributeName="transform"
          type="rotate"
          from={`${angle} ${cx} ${cy}`}
          to={`${angle} ${cx} ${cy}`}
          dur="0.5s"
          fill="freeze"
        />
      </line>

      {/* 中心圆 */}
      <circle cx={cx} cy={cy} r={3} fill="#f59e0b" />

      {/* 数字读数 */}
      <text
        x={cx}
        y={cy + 20}
        textAnchor="middle"
        fill="#f59e0b"
        fontSize={13}
        fontWeight="bold"
        fontFamily="monospace"
      >
        {clampRate.toFixed(1)}
      </text>
      <text
        x={cx}
        y={cy + 34}
        textAnchor="middle"
        fill="#94a3b8"
        fontSize={8}
      >
        L/min
      </text>

      {/* 量程标签 */}
      <text x={cx - radius + 2} y={cy + 4} fill="#64748b" fontSize={7} textAnchor="middle">0</text>
      <text x={cx + radius - 2} y={cy + 4} fill="#64748b" fontSize={7} textAnchor="middle">{maxRange}</text>
    </svg>
  )
}