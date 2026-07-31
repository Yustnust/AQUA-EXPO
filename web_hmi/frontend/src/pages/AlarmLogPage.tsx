import { useState, useEffect } from 'react'
import { useAlarmStore } from '../stores/alarmStore'
import { alarmApi, plcApi } from '../api/client'

export default function AlarmLogPage() {
  const [selectedUnit, setSelectedUnit] = useState<number | 'all'>('all')
  const [events, setEvents] = useState<Array<Record<string, unknown>>>([])
  const unitAlarms = useAlarmStore((s) => s.unitAlarms)

  useEffect(() => {
    const params: Record<string, unknown> = { minutes: 60, limit: 200 }
    if (selectedUnit !== 'all') params.unit_id = selectedUnit
    alarmApi.getEvents(params as never).then((res) => setEvents(res.events)).catch(() => {})
  }, [selectedUnit])

  const handleAck = async (unitId: number) => {
    try {
      await plcApi.writePulse(unitId, 'cmd_ack_alarm')
    } catch (err) {
      alert(err instanceof Error ? err.message : '确认失败')
    }
  }

  const handleMute = async (unitId: number) => {
    try {
      await plcApi.writePulse(unitId, 'cmd_mute')
    } catch (err) {
      alert(err instanceof Error ? err.message : '消音失败')
    }
  }

  // 当前活动报警
  const allActiveAlarms = Object.entries(unitAlarms).flatMap(
    ([unitId, data]) => data.active_alarms.map((a) => ({ ...a, unitId: Number(unitId) }))
  ).filter((a) => selectedUnit === 'all' || a.unitId === selectedUnit)

  return (
    <div>
      <h2 className="text-lg font-bold text-white mb-4">报警日志</h2>

      <div className="mb-4 flex items-center gap-3">
        <label className="text-sm text-slate-300">单元:</label>
        <select
          value={selectedUnit}
          onChange={(e) => setSelectedUnit(e.target.value === 'all' ? 'all' : Number(e.target.value))}
          className="px-3 py-1.5 bg-slate-700 border border-slate-600 rounded text-white text-sm"
        >
          <option value="all">全部单元</option>
          {Array.from({ length: 8 }, (_, i) => (
            <option key={i + 1} value={i + 1}>单元 {i + 1}</option>
          ))}
        </select>
      </div>

      {/* 活动报警 */}
      {allActiveAlarms.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-bold text-red-400 mb-2">当前活动报警 ({allActiveAlarms.length})</h3>
          <div className="space-y-1">
            {allActiveAlarms.map((a) => (
              <div
                key={`${a.unitId}-${a.bit_index}`}
                className="p-2 rounded text-xs flex items-center justify-between"
                style={{ backgroundColor: a.color + '20', borderLeft: `3px solid ${a.color}` }}
              >
                <div>
                  <span className="font-mono text-xs opacity-60 mr-2">单元{a.unitId} [{a.alarm_code}]</span>
                  {a.text}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleAck(a.unitId)}
                    className="px-2 py-0.5 bg-blue-600 rounded text-white text-xs"
                  >
                    确认
                  </button>
                  <button
                    onClick={() => handleMute(a.unitId)}
                    className="px-2 py-0.5 bg-slate-600 rounded text-white text-xs"
                  >
                    消音
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 32位报警指示灯阵列 */}
      <div className="mb-4">
        <h3 className="text-sm font-bold text-slate-300 mb-2">报警位阵列</h3>
        <div className="grid grid-cols-8 gap-1">
          {Array.from({ length: 32 }, (_, i) => {
            const isActive = allActiveAlarms.some((a) => a.bit_index === i)
            const alarm = allActiveAlarms.find((a) => a.bit_index === i)
            return (
              <div
                key={i}
                className={`p-1 text-center text-xs rounded border ${
                  isActive
                    ? alarm?.level === 'critical'
                      ? 'bg-red-700 border-red-500 text-white alarm-blink'
                      : 'bg-yellow-700 border-yellow-500 text-white'
                    : 'bg-slate-700 border-slate-600 text-slate-500'
                }`}
                title={alarm?.text ?? '预留'}
              >
                {i}
              </div>
            )
          })}
        </div>
      </div>

      {/* 历史事件 */}
      <div>
        <h3 className="text-sm font-bold text-slate-300 mb-2">最近事件</h3>
        <div className="bg-slate-800 rounded border border-slate-700 overflow-hidden">
          <table className="w-full text-xs">
            <thead className="bg-slate-700">
              <tr>
                <th className="text-left px-3 py-1.5 text-slate-300">时间</th>
                <th className="text-left px-3 py-1.5 text-slate-300">单元</th>
                <th className="text-left px-3 py-1.5 text-slate-300">报警码</th>
                <th className="text-left px-3 py-1.5 text-slate-300">动作</th>
                <th className="text-left px-3 py-1.5 text-slate-300">描述</th>
              </tr>
            </thead>
            <tbody>
              {events.slice(0, 50).map((evt, i) => (
                <tr key={i} className="border-t border-slate-700">
                  <td className="px-3 py-1.5 text-slate-400">{(evt.ts as string)?.slice(11, 19) ?? '-'}</td>
                  <td className="px-3 py-1.5 text-white">{String(evt.unit_id ?? '-')}</td>
                  <td className="px-3 py-1.5 font-mono text-white">{String(evt.alarm_code ?? '-')}</td>
                  <td className="px-3 py-1.5">
                    <span className={`px-1.5 py-0.5 rounded text-xs ${
                      evt.action === 'trigger' ? 'bg-red-800 text-red-300' :
                      evt.action === 'reset' ? 'bg-green-800 text-green-300' :
                      'bg-slate-600 text-slate-300'
                    }`}>
                      {evt.action === 'trigger' ? '触发' : evt.action === 'reset' ? '复位' : evt.action === 'mute' ? '消音' : String(evt.action)}
                    </span>
                  </td>
                  <td className="px-3 py-1.5 text-slate-300">{String(evt.alarm_text ?? '-')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}