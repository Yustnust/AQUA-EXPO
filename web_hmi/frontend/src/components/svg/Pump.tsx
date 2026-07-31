interface PumpProps {
  label: string
  /** 是否运行中 */
  running: boolean
  size?: number
}

export default function Pump({ label, running, size = 50 }: PumpProps) {
  const cx = size / 2
  const cy = size / 2
  const r = size / 2 - 6

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {/* 泵体外圈 */}
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill="none"
        stroke={running ? '#22c55e' : '#64748b'}
        strokeWidth={2}
      />

      {/* 叶轮 - 旋转 */}
      <g>
        {running && (
          <animateTransform
            attributeName="transform"
            type="rotate"
            from={`0 ${cx} ${cy}`}
            to={`360 ${cx} ${cy}`}
            dur="1.5s"
            repeatCount="indefinite"
          />
        )}
        {/* 叶片1 */}
        <line
          x1={cx}
          y1={cy - r + 4}
          x2={cx}
          y2={cy + r - 4}
          stroke={running ? '#22c55e' : '#475569'}
          strokeWidth={3}
          strokeLinecap="round"
        />
        {/* 叶片2 */}
        <line
          x1={cx - r + 4}
          y1={cy}
          x2={cx + r - 4}
          y2={cy}
          stroke={running ? '#22c55e' : '#475569'}
          strokeWidth={3}
          strokeLinecap="round"
        />
        {/* 中心圆 */}
        <circle cx={cx} cy={cy} r={3} fill={running ? '#16a34a' : '#475569'} />
      </g>

      {/* 运行指示灯 */}
      <circle
        cx={cx + r - 4}
        cy={cy - r + 4}
        r={3}
        fill={running ? '#22c55e' : '#475569'}
      >
        {running && (
          <animate
            attributeName="opacity"
            values="1;0.3;1"
            dur="1s"
            repeatCount="indefinite"
          />
        )}
      </circle>

      {/* 标签 */}
      <text
        x={cx}
        y={size - 2}
        textAnchor="middle"
        fill="#cbd5e1"
        fontSize={8}
        fontWeight="bold"
      >
        {label}
      </text>
    </svg>
  )
}