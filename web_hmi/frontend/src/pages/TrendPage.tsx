import { useState, useEffect } from 'react'
import { historyApi } from '../api/client'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface TrendVar {
  name: string
  note: string
  dtype: string
  group: string
}

export default function TrendPage() {
  const [selectedUnit, setSelectedUnit] = useState(1)
  const [variables, setVariables] = useState<TrendVar[]>([])
  const [selectedVars, setSelectedVars] = useState<string[]>(['flowrate_instant', 'current_inlet_volume'])
  const [minutes, setMinutes] = useState(60)
  const [chartData, setChartData] = useState<Array<Record<string, unknown>>>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    historyApi.getVariables().then(setVariables).catch(() => {})
  }, [])

  useEffect(() => {
    if (selectedVars.length === 0) return
    setLoading(true)
    historyApi.query(selectedUnit, selectedVars, undefined, undefined, minutes)
      .then((res) => {
        // 将按变量分组的数据转换为 Recharts 格式
        const timeMap: Record<string, Record<string, number>> = {}
        for (const [varName, points] of Object.entries(res.data)) {
          for (const point of points) {
            const ts = (point.ts as string).slice(11, 19) // HH:MM:SS
            if (!timeMap[ts]) timeMap[ts] = {}
            timeMap[ts][varName] = point.value
          }
        }
        const sorted = Object.entries(timeMap)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([ts, values]) => ({ time: ts, ...values }))
        setChartData(sorted)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [selectedUnit, selectedVars, minutes])

  const toggleVar = (name: string) => {
    setSelectedVars((prev) =>
      prev.includes(name) ? prev.filter((v) => v !== name) : [...prev, name]
    )
  }

  const COLORS = ['#3B82F6', '#EF4444', '#22C55E', '#F59E0B', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316']

  return (
    <div>
      <h2 className="text-lg font-bold text-white mb-4">趋势曲线</h2>

      <div className="flex items-center gap-4 mb-4">
        <div className="flex items-center gap-2">
          <label className="text-sm text-slate-300">单元:</label>
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
        <div className="flex items-center gap-2">
          <label className="text-sm text-slate-300">时间范围:</label>
          <select
            value={minutes}
            onChange={(e) => setMinutes(Number(e.target.value))}
            className="px-3 py-1.5 bg-slate-700 border border-slate-600 rounded text-white text-sm"
          >
            <option value={10}>10 分钟</option>
            <option value={60}>1 小时</option>
            <option value={480}>8 小时</option>
            <option value={1440}>24 小时</option>
          </select>
        </div>
      </div>

      {/* 变量选择 */}
      <div className="mb-4 flex flex-wrap gap-2">
        {variables.map((v) => (
          <button
            key={v.name}
            onClick={() => toggleVar(v.name)}
            className={`px-2 py-1 rounded text-xs transition-colors ${
              selectedVars.includes(v.name)
                ? 'bg-blue-600 text-white'
                : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
            }`}
            title={v.note}
          >
            {v.name}
          </button>
        ))}
      </div>

      {/* 图表 */}
      <div className="bg-slate-800 rounded border border-slate-700 p-4" style={{ height: 400 }}>
        {loading ? (
          <div className="flex items-center justify-center h-full text-slate-400">加载中...</div>
        ) : chartData.length === 0 ? (
          <div className="flex items-center justify-center h-full text-slate-500">选择变量查看趋势</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" stroke="#64748B" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748B" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#1E293B', border: '1px solid #475569', borderRadius: 4 }}
                labelStyle={{ color: '#E2E8F0' }}
              />
              <Legend />
              {selectedVars.map((v, i) => (
                <Line
                  key={v}
                  type="monotone"
                  dataKey={v}
                  stroke={COLORS[i % COLORS.length]}
                  dot={false}
                  strokeWidth={1.5}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}