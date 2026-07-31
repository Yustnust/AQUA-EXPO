import { useAlarmStore } from '../stores/alarmStore'

export default function AlarmBanner() {
  const unitAlarms = useAlarmStore((s) => s.unitAlarms)

  // 汇总所有单元的报警
  const allAlarms = Object.entries(unitAlarms).flatMap(
    ([unitId, data]) => data.active_alarms.map((a) => ({ ...a, unitId: Number(unitId) }))
  )

  if (allAlarms.length === 0) {
    return (
      <div className="h-7 bg-slate-800 flex items-center px-4 text-xs text-green-400 border-b border-slate-700">
        ● 系统正常 — 无报警
      </div>
    )
  }

  const criticalAlarms = allAlarms.filter((a) => a.level === 'critical' || a.level === 'overflow')
  const hasBlink = criticalAlarms.length > 0

  return (
    <div className={`h-7 flex items-center px-4 text-xs font-bold border-b border-slate-700 ${
      hasBlink
        ? 'bg-red-900 text-red-200 alarm-blink'
        : allAlarms.some((a) => a.level === 'rhythm')
          ? 'bg-orange-900 text-orange-200'
          : 'bg-yellow-900 text-yellow-200'
    }`}>
      <span className="mr-2">⚠</span>
      {allAlarms.length} 个活动报警
      {criticalAlarms.length > 0 && (
        <span className="ml-2">（含 {criticalAlarms.length} 个严重报警）</span>
      )}
      <span className="ml-auto text-xs opacity-70">
        {allAlarms.slice(0, 3).map((a) => `单元${a.unitId}: ${a.text}`).join(' | ')}
      </span>
    </div>
  )
}