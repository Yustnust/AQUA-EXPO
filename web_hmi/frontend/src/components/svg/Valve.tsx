interface ValveProps {
  label: string
  /** 阀门状态: true=开, false=关 */
  open: boolean
  /** 尺寸 */
  size?: number
  /** 方向: horizontal 水平管道, vertical 垂直管道 */
  orientation?: 'horizontal' | 'vertical'
}

export default function Valve({
  label,
  open,
  size = 40,
  orientation = 'horizontal',
}: ValveProps) {
  const half = size / 2
  const fillColor = open ? '#22c55e' : '#ef4444'
  const strokeColor = open ? '#16a34a' : '#dc2626'

  // 阀门符号: 两个三角形 + 中间直线
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {orientation === 'horizontal' ? (
        <>
          {/* 管道连接线 */}
          <line x1={0} y1={half} x2={half - 6} y2={half} stroke="#94a3b8" strokeWidth={2} />
          <line x1={half + 6} y1={half} x2={size} y2={half} stroke="#94a3b8" strokeWidth={2} />

          {/* 阀门体 - 菱形 */}
          <polygon
            points={`${half - 6},${half} ${half},${half - 8} ${half + 6},${half} ${half},${half + 8}`}
            fill={fillColor}
            stroke={strokeColor}
            strokeWidth={1.5}
          >
            {/* 开关切换动画 */}
            <animate
              attributeName="fill"
              values={`${open ? '#ef4444' : '#22c55e'};${open ? '#22c55e' : '#ef4444'}`}
              dur="0.3s"
              fill="freeze"
            />
          </polygon>
        </>
      ) : (
        <>
          {/* 管道连接线 */}
          <line x1={half} y1={0} x2={half} y2={half - 6} stroke="#94a3b8" strokeWidth={2} />
          <line x1={half} y1={half + 6} x2={half} y2={size} stroke="#94a3b8" strokeWidth={2} />

          {/* 阀门体 - 菱形 */}
          <polygon
            points={`${half},${half - 6} ${half - 8},${half} ${half},${half + 6} ${half + 8},${half}`}
            fill={fillColor}
            stroke={strokeColor}
            strokeWidth={1.5}
          >
            <animate
              attributeName="fill"
              values={`${open ? '#ef4444' : '#22c55e'};${open ? '#22c55e' : '#ef4444'}`}
              dur="0.3s"
              fill="freeze"
            />
          </polygon>
        </>
      )}

      {/* 标签 */}
      <text
        x={half}
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