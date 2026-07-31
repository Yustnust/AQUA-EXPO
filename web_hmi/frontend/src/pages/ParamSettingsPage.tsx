import { useState, useEffect } from 'react'
import { usePlcStore } from '../stores/plcStore'
import { plcApi } from '../api/client'
import ConfirmDialog from '../components/ConfirmDialog'

interface VariableInfo {
  name: string
  v_addr: number
  dtype: string
  writable: boolean
  note: string
}

export default function ParamSettingsPage() {
  const [selectedUnit, setSelectedUnit] = useState(1)
  const [variables, setVariables] = useState<VariableInfo[]>([])
  const [editValues, setEditValues] = useState<Record<string, string>>({})
  const [confirmVar, setConfirmVar] = useState<{ name: string; value: string } | null>(null)
  const units = usePlcStore((s) => s.units)
  const unitData = units[selectedUnit]?.data ?? {}

  useEffect(() => {
    plcApi.getVariables().then((vars) => {
      setVariables(vars.filter((v) => v.writable && v.dtype !== 'bool'))
    }).catch(() => {})
  }, [])

  const writableVars = variables.filter((v) => v.writable && v.dtype !== 'bool')

  const handleWrite = async () => {
    if (!confirmVar) return
    try {
      const value = confirmVar.value.includes('.')
        ? parseFloat(confirmVar.value)
        : parseInt(confirmVar.value)
      await plcApi.write(selectedUnit, confirmVar.name, value)
      setConfirmVar(null)
    } catch (err) {
      alert(err instanceof Error ? err.message : '写入失败')
    }
  }

  return (
    <div>
      <h2 className="text-lg font-bold text-white mb-4">参数设置</h2>

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
      </div>

      <div className="bg-slate-800 rounded border border-slate-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-700">
            <tr>
              <th className="text-left px-4 py-2 text-slate-300">参数</th>
              <th className="text-left px-4 py-2 text-slate-300">说明</th>
              <th className="text-left px-4 py-2 text-slate-300">当前值</th>
              <th className="text-left px-4 py-2 text-slate-300">新值</th>
              <th className="px-4 py-2"></th>
            </tr>
          </thead>
          <tbody>
            {writableVars.map((v) => {
              const currentVal = unitData[v.name]
              const displayVal = typeof currentVal === 'number' ? currentVal.toFixed(2) : '-'
              return (
                <tr key={v.name} className="border-t border-slate-700">
                  <td className="px-4 py-2 font-mono text-xs text-blue-400">{v.name}</td>
                  <td className="px-4 py-2 text-slate-400">{v.note}</td>
                  <td className="px-4 py-2 font-mono text-white">{displayVal}</td>
                  <td className="px-4 py-2">
                    <input
                      type="text"
                      value={editValues[v.name] ?? ''}
                      onChange={(e) => setEditValues({ ...editValues, [v.name]: e.target.value })}
                      className="w-28 px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-xs font-mono"
                      placeholder="新值"
                    />
                  </td>
                  <td className="px-4 py-2">
                    <button
                      onClick={() => setConfirmVar({ name: v.name, value: editValues[v.name] ?? '' })}
                      disabled={!editValues[v.name]}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded text-white text-xs"
                    >
                      写入
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {confirmVar && (
        <ConfirmDialog
          title="确认参数修改"
          message={`确认将单元 ${selectedUnit} 的 ${confirmVar.name} 修改为 ${confirmVar.value}？`}
          onConfirm={handleWrite}
          onCancel={() => setConfirmVar(null)}
          confirmText="确认修改"
          danger
        />
      )}
    </div>
  )
}