import { useAlarmStore } from '../stores/alarmStore'
import { plcApi } from '../api/client'

export default function AlarmPopup() {
  const { showPopup, popupUnit, unitAlarms, acknowledgePopup } = useAlarmStore()

  if (!showPopup || !popupUnit) return null

  const alarms = unitAlarms[popupUnit]?.active_alarms ?? []

  const handleAck = async () => {
    try {
      await plcApi.writePulse(popupUnit, 'cmd_ack_alarm')
    } catch {
      // ignore
    }
    acknowledgePopup()
  }

  const handleMute = async () => {
    try {
      await plcApi.writePulse(popupUnit, 'cmd_mute')
    } catch {
      // ignore
    }
  }

  return (
    <div className="alarm-overlay" onClick={acknowledgePopup}>
      <div
        className="bg-slate-800 border-2 border-red-500 rounded-lg p-6 max-w-lg w-full shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">⚠</span>
          <h2 className="text-lg font-bold text-red-400">新报警 — 单元 {popupUnit}</h2>
        </div>
        <div className="space-y-2 mb-4 max-h-60 overflow-auto">
          {alarms.map((a) => (
            <div
              key={a.bit_index}
              className="p-2 rounded text-sm"
              style={{ backgroundColor: a.color + '20', borderLeft: `3px solid ${a.color}` }}
            >
              <span className="font-mono text-xs opacity-60 mr-2">
                [{a.alarm_code}]
              </span>
              {a.text}
            </div>
          ))}
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleAck}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm font-bold"
          >
            报警确认
          </button>
          <button
            onClick={handleMute}
            className="flex-1 px-4 py-2 bg-slate-600 hover:bg-slate-500 rounded text-white text-sm"
          >
            消音
          </button>
          <button
            onClick={acknowledgePopup}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-slate-300 text-sm"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  )
}