import { useState } from 'react'
import { usePlcStore } from '../stores/plcStore'
import { plcApi } from '../api/client'
import ConfirmDialog from '../components/ConfirmDialog'

export default function ManualControlPage() {
  const units = usePlcStore((s) => s.units)
  const [selectedUnit, setSelectedUnit] = useState(1)
  const [confirmAction, setConfirmAction] = useState<{ label: string; cmd: string } | null>(null)

  const handleCommand = async (cmd: string) => {
    try {
      await plcApi.writePulse(selectedUnit, cmd)
    } catch (err) {
      alert(err instanceof Error ? err.message : '命令失败')
    }
  }

  const manualActions = [
    { label: '开阀A', cmd: 'cmd_manual_valve_a_open', color: 'bg-green-600' },
    { label: '关阀A', cmd: 'cmd_manual_valve_a_close', color: 'bg-red-600' },
    { label: '开阀B', cmd: 'cmd_manual_valve_b_open', color: 'bg-green-600' },
    { label: '关阀B', cmd: 'cmd_manual_valve_b_close', color: 'bg-red-600' },
    { label: '开阀C', cmd: 'cmd_manual_valve_c_open', color: 'bg-green-600' },
    { label: '关阀C', cmd: 'cmd_manual_valve_c_close', color: 'bg-red-600' },
    { label: '启动潜水泵1', cmd: 'cmd_manual_pump1_on', color: 'bg-blue-600' },
    { label: '停止潜水泵1', cmd: 'cmd_manual_pump1_off', color: 'bg-red-600' },
  ]

  return (
    <div>
      <h2 className="text-lg font-bold text-white mb-4">手动控制</h2>

      <div className="mb-4 flex items-center gap-3">
        <label className="text-sm text-slate-300">选择单元:</label>
        <select
          value={selectedUnit}
          onChange={(e) => setSelectedUnit(Number(e.target.value))}
          className="px-3 py-1.5 bg-slate-700 border border-slate-600 rounded text-white text-sm"
        >
          {Array.from({ length: 8 }, (_, i) => (
            <option key={i + 1} value={i + 1}>单元 {i + 1}</option>
          ))}
        </select>
        <span className={`px-2 py-0.5 rounded text-xs ${
          units[selectedUnit]?.connected ? 'bg-green-800 text-green-300' : 'bg-red-800 text-red-300'
        }`}>
          {units[selectedUnit]?.connected ? '在线' : '离线'}
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {manualActions.map((action) => (
          <button
            key={action.cmd}
            onClick={() => setConfirmAction(action)}
            className={`${action.color} hover:opacity-90 rounded p-4 text-white text-sm font-bold text-center transition-opacity`}
          >
            {action.label}
          </button>
        ))}
      </div>

      {confirmAction && (
        <ConfirmDialog
          title="确认操作"
          message={`确认对单元 ${selectedUnit} 执行：${confirmAction.label}？`}
          onConfirm={async () => {
            await handleCommand(confirmAction.cmd)
            setConfirmAction(null)
          }}
          onCancel={() => setConfirmAction(null)}
          confirmText={confirmAction.label}
          danger={confirmAction.cmd.includes('close') || confirmAction.cmd.includes('off')}
        />
      )}
    </div>
  )
}