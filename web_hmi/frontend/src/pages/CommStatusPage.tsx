import { useState, useEffect } from 'react'
import { plcApi } from '../api/client'

interface PlcStatus {
  unit: number
  connected: boolean
  host: string
  port: number
}

export default function CommStatusPage() {
  const [statuses, setStatuses] = useState<PlcStatus[]>([])
  const [loading, setLoading] = useState(true)

  const fetchStatus = async () => {
    setLoading(true)
    try {
      const res = await plcApi.getStatus()
      setStatuses(res.units)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-white">通讯维护</h2>
        <button
          onClick={fetchStatus}
          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm"
        >
          {loading ? '刷新中...' : '刷新'}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {statuses.map((s) => (
          <div
            key={s.unit}
            className={`p-4 rounded-lg border-2 ${
              s.connected
                ? 'border-green-600 bg-slate-800'
                : 'border-red-600 bg-red-900/20'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold text-white">单元 {s.unit}</span>
              <span className={`w-3 h-3 rounded-full ${
                s.connected ? 'bg-green-500' : 'bg-red-500'
              }`} />
            </div>
            <div className="text-xs text-slate-400 space-y-1">
              <div>IP: {s.host}</div>
              <div>端口: {s.port}</div>
              <div className={s.connected ? 'text-green-400' : 'text-red-400'}>
                {s.connected ? '● 通讯正常' : '● 通讯中断'}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}