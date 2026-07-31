import { useNavigate } from 'react-router-dom'
import { usePlcStore } from '../stores/plcStore'
import { useAlarmStore } from '../stores/alarmStore'

const UNIT_NAMES = Array.from({ length: 8 }, (_, i) => `单元${i + 1}`)

/** 状态机简称 */
const SM_SHORT: Record<number, string> = {
  0: '空闲', 1: '进水', 2: '预循环', 3: '浓度检测',
  4: '静止', 5: '转移', 6: '运行', 7: '排水',
}

export default function OverviewPage() {
  const navigate = useNavigate()
  const units = usePlcStore((s) => s.units)
  const unitAlarms = useAlarmStore((s) => s.unitAlarms)

  return (
    <div>
      <h2 className="text-lg font-bold text-white mb-4">系统总览</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 8 }, (_, i) => {
          const unitId = i + 1
          const unit = units[unitId]
          const alarms = unitAlarms[unitId]?.active_alarms ?? []
          const hasAlarm = alarms.length > 0
          const hasCritical = alarms.some((a) => a.level === 'critical' || a.level === 'overflow')
          const connected = unit?.connected ?? false
          const data = unit?.data ?? {}

          const sm = Number(data.state_machine ?? 0)
          const flowRate = Number(data.flowrate_instant ?? 0)
          const tankAFull = Boolean(data.sta_tank_a_state)
          const tankBFull = Boolean(data.sta_tank_b_state)
          const inletVol = Number(data.current_inlet_volume ?? 0)
          const targetVol = Number(data.target_inlet_volume ?? 0)

          // 上缸液位
          const tankALevel = tankAFull ? 100
            : (targetVol > 0 ? Math.min(100, (inletVol / targetVol) * 100) : 0)
          const tankBLevel = tankBFull ? 100 : 0

          return (
            <button
              key={unitId}
              onClick={() => navigate(`/unit/${unitId}`)}
              className={`p-4 rounded-lg border-2 text-left transition-all hover:scale-[1.02] ${
                !connected
                  ? 'border-slate-600 bg-slate-800/50'
                  : hasCritical
                    ? 'border-red-500 bg-red-900/30 alarm-blink'
                    : hasAlarm
                      ? 'border-yellow-500 bg-yellow-900/20'
                      : 'border-green-600 bg-slate-800'
              }`}
            >
              {/* 头部：名称 + 连接状态 */}
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-white">{UNIT_NAMES[i]}</span>
                <span className={`w-2.5 h-2.5 rounded-full ${
                  connected ? 'bg-green-500' : 'bg-slate-600'
                }`} />
              </div>

              {connected && data ? (
                <div className="space-y-2">
                  {/* 简化水缸动画 */}
                  <div className="flex items-center gap-3 justify-center">
                    <MiniTank level={tankALevel} label="上" />
                    <MiniTank level={tankBLevel} label="下" />
                  </div>

                  {/* 状态信息 */}
                  <div className="text-xs space-y-0.5">
                    <div className="flex justify-between">
                      <span className="text-slate-400">{SM_SHORT[sm] ?? `S${sm}`}</span>
                      <span className="text-slate-400">
                        {flowRate > 0 ? `${flowRate.toFixed(1)} L/min` : '无流量'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">报警码</span>
                      <span className={hasAlarm ? 'text-red-400 font-bold font-mono' : 'text-green-400 font-mono'}>
                        {String(data.alarm_code ?? 0)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">进水量</span>
                      <span className="text-blue-400 font-mono">
                        {inletVol > 0 ? `${inletVol.toFixed(1)} L` : '-'}
                      </span>
                    </div>
                  </div>

                  {hasAlarm && (
                    <div className="text-red-400 text-xs font-bold animate-pulse">
                      {alarms.length} 个报警
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-xs text-slate-500 text-center py-3">通讯中断</div>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}

/** 简化小水缸图标 */
function MiniTank({ level, label }: { level: number; label: string }) {
  const w = 24
  const h = 36
  const clampLvl = Math.max(0, Math.min(100, level))
  const waterH = (clampLvl / 100) * (h - 6)
  const waterY = h - 2 - waterH
  const color = clampLvl > 80 ? '#3b82f6' : clampLvl > 30 ? '#60a5fa' : '#334155'

  return (
    <div className="flex flex-col items-center gap-0.5">
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
        <rect x={1} y={1} width={w - 2} height={h - 2} rx={2} fill="none" stroke="#475569" strokeWidth={1} />
        <rect x={2} y={waterY} width={w - 4} height={waterH} rx={1} fill={color} opacity={0.8}>
          {level > 0 && level < 100 && (
            <animate attributeName="height" values={`${waterH}`} dur="0.5s" />
          )}
        </rect>
      </svg>
      <span className="text-[9px] text-slate-500">{label}</span>
    </div>
  )
}