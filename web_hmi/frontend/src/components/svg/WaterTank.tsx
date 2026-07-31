import { useMemo } from 'react'

interface WaterTankProps {
  label: string
  /** 液位百分比 0~100 */
  level: number
  /** 宽度 */
  width?: number
  /** 高度 */
  height?: number
  /** 是否在进水/排水 */
  flowing?: boolean
}

export default function WaterTank({
  label,
  level,
  width = 90,
  height = 140,
  flowing = false,
}: WaterTankProps) {
  const clampLevel = Math.max(0, Math.min(100, level))
  const waterHeight = (clampLevel / 100) * (height - 16)
  const waterY = height - 4 - waterHeight

  // 根据液位颜色变化
  const waterColor = clampLevel > 80 ? '#3b82f6' : clampLevel > 30 ? '#60a5fa' : '#93c5fd'

  const waveId = useMemo(() => `wave-${label}-${Math.random().toString(36).slice(2, 6)}`, [label])

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      {/* 缸体轮廓 */}
      <rect
        x={2}
        y={2}
        width={width - 4}
        height={height - 4}
        rx={4}
        fill="none"
        stroke="#64748b"
        strokeWidth={1.5}
      />

      {/* 液位区域 - clipPath */}
      <defs>
        <clipPath id={waveId}>
          <rect x={3} y={waterY} width={width - 6} height={waterHeight + 1} rx={2} />
        </clipPath>
      </defs>

      {/* 液位填充 */}
      <g clipPath={`url(#${waveId})`}>
        <rect
          x={3}
          y={waterY}
          width={width - 6}
          height={waterHeight}
          fill={waterColor}
          opacity={0.85}
        />
        {/* 水面波纹 */}
        {flowing && (
          <path
            d={`M 3 ${waterY + 6} Q ${width / 4} ${waterY - 2} ${width / 2} ${waterY + 6} T ${width - 3} ${waterY + 6}`}
            fill="none"
            stroke="rgba(255,255,255,0.5)"
            strokeWidth={1.5}
          >
            <animateTransform
              attributeName="transform"
              type="translate"
              values={`0,0;${width / 2},0;${width},0`}
              dur="2s"
              repeatCount="indefinite"
            />
          </path>
        )}
      </g>

      {/* 液位百分比文字 */}
      <text
        x={width / 2}
        y={height / 2 + 4}
        textAnchor="middle"
        fill="white"
        fontSize={11}
        fontWeight="bold"
        style={{ textShadow: '0 1px 3px rgba(0,0,0,0.6)' }}
      >
        {clampLevel.toFixed(0)}%
      </text>

      {/* 标签 */}
      <text
        x={width / 2}
        y={height - 8}
        textAnchor="middle"
        fill="#94a3b8"
        fontSize={9}
      >
        {label}
      </text>

      {/* 进水/排水指示 */}
      {flowing && (
        <text
          x={width / 2}
          y={14}
          textAnchor="middle"
          fill="#60a5fa"
          fontSize={8}
        >
          ▸ 流动中
        </text>
      )}
    </svg>
  )
}