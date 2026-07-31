interface PipeFlowProps {
  /** 是否流动 */
  flowing: boolean
  /** 方向 */
  direction?: 'horizontal' | 'vertical'
  /** 长度 */
  length?: number
  /** 颜色 */
  color?: string
}

export default function PipeFlow({
  flowing,
  direction = 'horizontal',
  length = 60,
  color = '#3b82f6',
}: PipeFlowProps) {
  const w = direction === 'horizontal' ? length : 12
  const h = direction === 'horizontal' ? 12 : length

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      {direction === 'horizontal' ? (
        <>
          {/* 管道线 */}
          <line
            x1={0}
            y1={h / 2}
            x2={w}
            y2={h / 2}
            stroke={flowing ? color : '#475569'}
            strokeWidth={3}
            strokeLinecap="round"
          />
          {/* 流动虚线 */}
          {flowing && (
            <line
              x1={0}
              y1={h / 2}
              x2={w}
              y2={h / 2}
              stroke="rgba(255,255,255,0.7)"
              strokeWidth={2}
              strokeDasharray="6 4"
              strokeLinecap="round"
            >
              <animate
                attributeName="stroke-dashoffset"
                values="0;-20"
                dur="0.6s"
                repeatCount="indefinite"
              />
            </line>
          )}
          {/* 箭头 */}
          {flowing && (
            <polygon
              points={`${w - 2},${h / 2} ${w - 8},${h / 2 - 4} ${w - 8},${h / 2 + 4}`}
              fill={color}
            />
          )}
        </>
      ) : (
        <>
          {/* 管道线 */}
          <line
            x1={w / 2}
            y1={0}
            x2={w / 2}
            y2={h}
            stroke={flowing ? color : '#475569'}
            strokeWidth={3}
            strokeLinecap="round"
          />
          {/* 流动虚线 */}
          {flowing && (
            <line
              x1={w / 2}
              y1={0}
              x2={w / 2}
              y2={h}
              stroke="rgba(255,255,255,0.7)"
              strokeWidth={2}
              strokeDasharray="6 4"
              strokeLinecap="round"
            >
              <animate
                attributeName="stroke-dashoffset"
                values="0;-20"
                dur="0.6s"
                repeatCount="indefinite"
              />
            </line>
          )}
          {/* 箭头 */}
          {flowing && (
            <polygon
              points={`${w / 2},${h - 2} ${w / 2 - 4},${h - 8} ${w / 2 + 4},${h - 8}`}
              fill={color}
            />
          )}
        </>
      )}
    </svg>
  )
}