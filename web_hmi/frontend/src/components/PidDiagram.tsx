interface PidDiagramProps {
  /** 上缸液位 0~100 */
  tankALevel: number
  /** 下缸液位 0~100 */
  tankBLevel: number
  /** 阀A开 */
  valveAOpen: boolean
  /** 阀B开 */
  valveBOpen: boolean
  /** 阀C开 */
  valveCOpen: boolean
  /** 潜水泵运行 */
  pump1Running: boolean
  /** 注射泵运行 */
  syringePumpRunning: boolean
  /** 瞬时流速 */
  flowRate: number
  /** 状态机 */
  stateMachine: number
  /** 是否有水流 */
  hasFlow: boolean
}

/**
 * 计算流速对应的指针角度
 */
function flowAngle(rate: number): number {
  const clamped = Math.max(0, Math.min(rate, 25))
  return -90 + (clamped / 25) * 180
}

/**
 * 绘制菱形阀门
 */
function ValveSymbol({
  cx, cy, open, label,
}: { cx: number; cy: number; open: boolean; label: string }) {
  const color = open ? '#22c55e' : '#ef4444'
  const stroke = open ? '#16a34a' : '#dc2626'
  return (
    <g>
      <polygon
        points={`${cx - 10},${cy} ${cx},${cy - 8} ${cx + 10},${cy} ${cx},${cy + 8}`}
        fill={color}
        stroke={stroke}
        strokeWidth={1.2}
      />
      <text x={cx} y={cy - 12} textAnchor="middle" fill="#94a3b8" fontSize={8} fontWeight="bold">
        {label}
      </text>
    </g>
  )
}

/**
 * 绘制水缸
 */
function TankSymbol({
  x, y, w, h, level, label, flowing,
}: { x: number; y: number; w: number; h: number; level: number; label: string; flowing: boolean }) {
  const clampLvl = Math.max(0, Math.min(100, level))
  const waterH = (clampLvl / 100) * (h - 8)
  const waterY = y + h - 4 - waterH
  const waterColor = clampLvl > 80 ? '#3b82f6' : clampLvl > 30 ? '#60a5fa' : '#93c5fd'
  const clipId = `tank-clip-${label}`

  return (
    <g>
      {/* 缸体 */}
      <rect x={x} y={y} width={w} height={h} rx={4} fill="none" stroke="#64748b" strokeWidth={1.5} />
      {/* 液位 */}
      <defs>
        <clipPath id={clipId}>
          <rect x={x + 2} y={waterY} width={w - 4} height={waterH + 2} rx={2} />
        </clipPath>
      </defs>
      <g clipPath={`url(#${clipId})`}>
        <rect x={x + 2} y={waterY} width={w - 4} height={waterH} fill={waterColor} opacity={0.85} />
        {flowing && (
          <path
            d={`M ${x + 2} ${waterY + 5} Q ${x + w / 4} ${waterY - 1} ${x + w / 2} ${waterY + 5} T ${x + w - 2} ${waterY + 5}`}
            fill="none"
            stroke="rgba(255,255,255,0.4)"
            strokeWidth={1.5}
          >
            <animateTransform
              attributeName="transform"
              type="translate"
              values={`0,0;${w / 2},0;${w},0`}
              dur="2s"
              repeatCount="indefinite"
            />
          </path>
        )}
      </g>
      {/* 液位数字 */}
      <text x={x + w / 2} y={y + h / 2 + 4} textAnchor="middle" fill="white" fontSize={11} fontWeight="bold"
        style={{ textShadow: '0 1px 3px rgba(0,0,0,0.6)' }}>
        {clampLvl.toFixed(0)}%
      </text>
      {/* 标签 */}
      <text x={x + w / 2} y={y + h + 14} textAnchor="middle" fill="#94a3b8" fontSize={10} fontWeight="bold">
        {label}
      </text>
    </g>
  )
}

/**
 * 绘制泵
 */
function PumpSymbol({
  cx, cy, r, running, label,
}: { cx: number; cy: number; r: number; running: boolean; label: string }) {
  return (
    <g>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke={running ? '#22c55e' : '#64748b'} strokeWidth={2} />
      <g>
        {running && (
          <animateTransform attributeName="transform" type="rotate"
            from={`0 ${cx} ${cy}`} to={`360 ${cx} ${cy}`} dur="1.5s" repeatCount="indefinite" />
        )}
        <line x1={cx} y1={cy - r + 4} x2={cx} y2={cy + r - 4} stroke={running ? '#22c55e' : '#475569'} strokeWidth={3} strokeLinecap="round" />
        <line x1={cx - r + 4} y1={cy} x2={cx + r - 4} y2={cy} stroke={running ? '#22c55e' : '#475569'} strokeWidth={3} strokeLinecap="round" />
        <circle cx={cx} cy={cy} r={3} fill={running ? '#16a34a' : '#475569'} />
      </g>
      <text x={cx} y={cy + r + 12} textAnchor="middle" fill="#94a3b8" fontSize={8} fontWeight="bold">
        {label}
      </text>
    </g>
  )
}

/**
 * 绘制流动管道
 */
function FlowLine({
  x1, y1, x2, y2, flowing,
}: { x1: number; y1: number; x2: number; y2: number; flowing: boolean }) {
  return (
    <g>
      <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={flowing ? '#3b82f6' : '#475569'} strokeWidth={3} strokeLinecap="round" />
      {flowing && (
        <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(255,255,255,0.6)" strokeWidth={2}
          strokeDasharray="6 5" strokeLinecap="round">
          <animate attributeName="stroke-dashoffset" values="0;-22" dur="0.5s" repeatCount="indefinite" />
        </line>
      )}
    </g>
  )
}

/**
 * 绘制流量计
 */
function FlowGaugeSymbol({
  cx, cy, r, rate,
}: { cx: number; cy: number; r: number; rate: number }) {
  const angle = flowAngle(rate)
  const rad = angle * Math.PI / 180

  // 刻度
  const ticks = []
  for (let i = 0; i <= 10; i++) {
    const a = (-90 + i * 18) * Math.PI / 180
    const innerR = r - 8
    const outerR = i % 5 === 0 ? r - 2 : r - 5
    ticks.push(
      <line key={i} x1={cx + innerR * Math.cos(a)} y1={cy + innerR * Math.sin(a)}
        x2={cx + outerR * Math.cos(a)} y2={cy + outerR * Math.sin(a)}
        stroke="#94a3b8" strokeWidth={i % 5 === 0 ? 1.2 : 0.7} />
    )
  }

  return (
    <g>
      {/* 圆弧 */}
      <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
        fill="none" stroke="#334155" strokeWidth={2} />
      {ticks}
      {/* 指针 */}
      <line x1={cx} y1={cy} x2={cx + (r - 12) * Math.cos(rad)} y2={cy + (r - 12) * Math.sin(rad)}
        stroke="#f59e0b" strokeWidth={2} strokeLinecap="round" />
      <circle cx={cx} cy={cy} r={3} fill="#f59e0b" />
      {/* 读数 */}
      <text x={cx} y={cy + 18} textAnchor="middle" fill="#f59e0b" fontSize={11} fontWeight="bold" fontFamily="monospace">
        {rate.toFixed(1)}
      </text>
      <text x={cx} y={cy + 30} textAnchor="middle" fill="#64748b" fontSize={8}>L/min</text>
    </g>
  )
}

export default function PidDiagram({
  tankALevel,
  tankBLevel,
  valveAOpen,
  valveBOpen,
  valveCOpen,
  pump1Running,
  syringePumpRunning,
  flowRate,
  stateMachine,
  hasFlow,
}: PidDiagramProps) {
  const svgW = 680
  const svgH = 360

  // 布局坐标
  const tankAY = 30
  const tankAX = 280
  const tankW = 80
  const tankH = 130

  const tankBX = 480
  const tankBY = tankAY
  

  const midY = tankAY + tankH / 2 // 管道中线

  return (
    <svg viewBox={`0 0 ${svgW} ${svgH}`} className="w-full h-auto max-w-[680px]">
      {/* ===== 管道连接 ===== */}

      {/* 水源 → 阀A */}
      <FlowLine x1={30} y1={midY} x2={130} y2={midY} flowing={hasFlow && valveAOpen} />
      {/* 水源标签 */}
      <text x={30} y={midY - 12} textAnchor="middle" fill="#94a3b8" fontSize={9}>水源</text>

      {/* 阀A → 流量计 */}
      <FlowLine x1={150} y1={midY} x2={220} y2={midY} flowing={hasFlow && valveAOpen} />

      {/* 流量计 → 上缸 */}
      <FlowLine x1={260} y1={midY} x2={tankAX + 10} y2={midY} flowing={hasFlow && valveAOpen} />

      {/* 上缸 → 阀B */}
      <FlowLine x1={tankAX + tankW} y1={midY} x2={tankBX - 10} y2={midY} flowing={hasFlow && valveBOpen} />

      {/* 阀B → 下缸 */}
      <FlowLine x1={tankBX + 10} y1={midY} x2={tankBX + tankW} y2={midY} flowing={hasFlow && valveBOpen} />

      {/* 下缸 → 阀C */}
      <FlowLine x1={tankBX + tankW} y1={midY} x2={620} y2={midY} flowing={hasFlow && valveCOpen} />

      {/* 阀C → 排水 */}
      <FlowLine x1={640} y1={midY} x2={660} y2={midY} flowing={hasFlow && valveCOpen} />
      <text x={660} y={midY - 12} textAnchor="middle" fill="#94a3b8" fontSize={9}>排水</text>

      {/* 注射泵 → 上缸 (垂直管道) */}
      <FlowLine x1={tankAX + tankW / 2} y1={midY + tankH / 2} x2={tankAX + tankW / 2} y2={240} flowing={hasFlow && syringePumpRunning} />

      {/* 潜水泵1 → 上缸 (垂直管道) */}
      <FlowLine x1={tankAX + tankW / 2 - 30} y1={midY + tankH / 2} x2={tankAX + tankW / 2 - 30} y2={240} flowing={hasFlow && pump1Running} />

      {/* ===== 阀门 ===== */}
      <ValveSymbol cx={140} cy={midY} open={valveAOpen} label="阀A" />
      <ValveSymbol cx={tankAX + tankW + 10} cy={midY} open={valveBOpen} label="阀B" />
      <ValveSymbol cx={630} cy={midY} open={valveCOpen} label="阀C" />

      {/* ===== 流量计 ===== */}
      <FlowGaugeSymbol cx={240} cy={midY - 10} r={24} rate={flowRate} />

      {/* ===== 水缸 ===== */}
      <TankSymbol x={tankAX} y={tankAY} w={tankW} h={tankH} level={tankALevel} label="上缸" flowing={hasFlow && valveAOpen} />
      <TankSymbol x={tankBX} y={tankBY} w={tankW} h={tankH} level={tankBLevel} label="下缸" flowing={hasFlow && valveBOpen} />

      {/* ===== 泵 ===== */}
      <PumpSymbol cx={tankAX + tankW / 2 - 30} cy={270} r={20} running={pump1Running} label="潜水泵1" />
      <PumpSymbol cx={tankAX + tankW / 2} cy={270} r={20} running={syringePumpRunning} label="注射泵" />

      {/* ===== 状态机指示 ===== */}
      <rect x={10} y={svgH - 40} width={120} height={30} rx={4} fill="none" stroke="#475569" strokeWidth={1} />
      <text x={70} y={svgH - 22} textAnchor="middle" fill="#94a3b8" fontSize={9}>状态机</text>
      <text x={70} y={svgH - 10} textAnchor="middle" fill="#60a5fa" fontSize={13} fontWeight="bold" fontFamily="monospace">
        S{stateMachine}
      </text>
    </svg>
  )
}