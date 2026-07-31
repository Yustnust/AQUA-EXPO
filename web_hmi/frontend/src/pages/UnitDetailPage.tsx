import { useParams, useNavigate } from 'react-router-dom'
import { usePlcStore } from '../stores/plcStore'
import { useAlarmStore } from '../stores/alarmStore'
import { plcApi } from '../api/client'
import { useState, useMemo } from 'react'
import ConfirmDialog from '../components/ConfirmDialog'
import PidDiagram from '../components/PidDiagram'

/** 状态机映射 */
const STATE_NAMES: Record<number, string> = {
  0: '空闲',
  1: 'S1 上缸进水',
  2: 'S2 预循环',
  3: 'S3 浓度检测',
  4: 'S3.5 静止等候',
  5: 'S4 上→下转移',
  6: 'S5 实验运行',
  7: 'S6 下缸排水',
}

export default function UnitDetailPage() {
  const { unitId } = useParams<{ unitId: string }>()
  const id = Number(unitId)
  const navigate = useNavigate()
  const unit = usePlcStore((s) => s.units[id])
  const alarms = useAlarmStore((s) => s.unitAlarms[id])
  const [showConfirm, setShowConfirm] = useState<'start' | 'stop' | null>(null)

  if (!unit) {
    return (
      <div className="text-center text-slate-400 py-10">
        单元 {id} 无数据
      </div>
    )
  }

  const data = unit.data ?? {}
  const activeAlarms = alarms?.active_alarms ?? []
  const sm = Number(data.state_machine ?? 0)
  const flowRate = Number(data.flowrate_instant ?? 0)
  const inletVol = Number(data.current_inlet_volume ?? 0)
  const targetVol = Number(data.target_inlet_volume ?? 0)
  const tankAFull = Boolean(data.sta_tank_a_state)
  const tankBFull = Boolean(data.sta_tank_b_state)
  const pumpStatus = Number(data.pump_status ?? 0)

  // 根据状态机推断阀门/泵/流动状态
  const pidState = useMemo(() => {
    // 上缸液位: 满=100%, 空时按进水量/目标量计算
    const tankALevel = tankAFull ? 100
      : (targetVol > 0 ? Math.min(100, (inletVol / targetVol) * 100) : 0)

    // 下缸液位: 当前只有满/空状态
    const tankBLevel = tankBFull ? 100 : 0

    // 阀门状态推断
    const valveAOpen = sm === 1  // S1 上缸进水
    const valveBOpen = sm === 5  // S4 上→下转移
    const valveCOpen = sm === 7  // S6 下缸排水

    // 泵状态
    const pump1Running = sm === 2  // S2 预循环
    const syringePumpRunning = pumpStatus > 0

    // 水流状态
    const hasFlow = flowRate > 0.05 || valveAOpen || valveBOpen || valveCOpen

    return {
      tankALevel,
      tankBLevel,
      valveAOpen,
      valveBOpen,
      valveCOpen,
      pump1Running,
      syringePumpRunning,
      hasFlow,
    }
  }, [sm, tankAFull, tankBFull, inletVol, targetVol, flowRate, pumpStatus])

  const handleCommand = async (cmd: string) => {
    try {
      await plcApi.writePulse(id, cmd)
    } catch (err) {
      alert(err instanceof Error ? err.message : '命令失败')
    }
  }

  const handleConfirm = async () => {
    if (showConfirm === 'start') await handleCommand('cmd_start')
    if (showConfirm === 'stop') await handleCommand('cmd_stop')
    setShowConfirm(null)
  }

  return (
    <div>
      {/* 标题栏 */}
      <div className="flex items-center gap-3 mb-4">
        <button onClick={() => navigate('/')} className="text-slate-400 hover:text-white">
          ← 返回总览
        </button>
        <h2 className="text-lg font-bold text-white">单元 {id} 详情</h2>
        <span className={`px-2 py-0.5 rounded text-xs ${unit.connected ? 'bg-green-800 text-green-300' : 'bg-red-800 text-red-300'}`}>
          {unit.connected ? '在线' : '离线'}
        </span>
        <span className="text-xs text-slate-400 ml-auto">
          {STATE_NAMES[sm] ?? `状态 ${sm}`}
        </span>
      </div>

      {/* P&ID 流程图 */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-3 mb-4 flex justify-center">
        <PidDiagram
          tankALevel={pidState.tankALevel}
          tankBLevel={pidState.tankBLevel}
          valveAOpen={pidState.valveAOpen}
          valveBOpen={pidState.valveBOpen}
          valveCOpen={pidState.valveCOpen}
          pump1Running={pidState.pump1Running}
          syringePumpRunning={pidState.syringePumpRunning}
          flowRate={flowRate}
          stateMachine={sm}
          hasFlow={pidState.hasFlow}
        />
      </div>

      {/* 状态概览 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <InfoCard label="状态机" value={STATE_NAMES[sm] ?? String(sm)} />
        <InfoCard label="报警码" value={String(data.alarm_code ?? 0)} danger={Number(data.alarm_code) > 0} />
        <InfoCard label="瞬时流速" value={flowRate > 0 ? `${flowRate.toFixed(1)} L/min` : '-'} />
        <InfoCard label="本次进水量" value={inletVol > 0 ? `${inletVol.toFixed(1)} L` : '-'} />
        <InfoCard label="目标进水量" value={targetVol > 0 ? `${targetVol.toFixed(1)} L` : '-'} />
        <InfoCard label="实验轮次" value={String(data.round_count ?? '-')} />
        <InfoCard label="注射泵状态" value={pumpStatus > 0 ? '运行中' : '停止'} />
        <InfoCard label="实验时长" value={typeof data.experiment_duration_accum === 'number' ? `${data.experiment_duration_accum.toFixed(1)} min` : '-'} />
      </div>

      {/* 命令按钮 */}
      <div className="flex gap-3 mb-4">
        <button
          onClick={() => setShowConfirm('start')}
          disabled={sm !== 0}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-40 disabled:cursor-not-allowed rounded text-white text-sm font-bold"
        >
          启动
        </button>
        <button
          onClick={() => setShowConfirm('stop')}
          disabled={sm === 0}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-40 disabled:cursor-not-allowed rounded text-white text-sm font-bold"
        >
          停止
        </button>
        <button
          onClick={() => handleCommand('cmd_mute')}
          className="px-4 py-2 bg-slate-600 hover:bg-slate-500 rounded text-white text-sm"
        >
          消音
        </button>
        <button
          onClick={() => handleCommand('cmd_ack_alarm')}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm"
        >
          报警确认
        </button>
      </div>

      {/* 声光报警状态 */}
      <div className="flex gap-4 mb-4 text-xs">
        <span className={`px-2 py-1 rounded ${data.sta_mute_done ? 'bg-green-800 text-green-300' : 'bg-slate-700 text-slate-400'}`}>
          声音: {data.sta_mute_done ? '已消音' : '鸣响中'}
        </span>
        <span className={`px-2 py-1 rounded ${activeAlarms.length > 0 ? 'bg-red-800 text-red-300 animate-pulse' : 'bg-green-800 text-green-300'}`}>
          灯光: {activeAlarms.length > 0 ? '报警中' : '正常'}
        </span>
      </div>

      {/* 活动报警 */}
      {activeAlarms.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-bold text-red-400 mb-2">活动报警 ({activeAlarms.length})</h3>
          <div className="space-y-1">
            {activeAlarms.map((a) => (
              <div
                key={a.bit_index}
                className="p-2 rounded text-xs"
                style={{ backgroundColor: a.color + '20', borderLeft: `3px solid ${a.color}` }}
              >
                [{a.alarm_code}] {a.text}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 二次确认弹窗 */}
      {showConfirm && (
        <ConfirmDialog
          title={showConfirm === 'start' ? '确认启动' : '确认停止'}
          message={showConfirm === 'start' ? `确认启动单元 ${id} 的实验？` : `确认停止单元 ${id} 的实验？`}
          onConfirm={handleConfirm}
          onCancel={() => setShowConfirm(null)}
          confirmText={showConfirm === 'start' ? '确认启动' : '确认停止'}
          danger={showConfirm === 'stop'}
        />
      )}
    </div>
  )
}

function InfoCard({ label, value, danger }: { label: string; value: string; danger?: boolean }) {
  return (
    <div className="bg-slate-800 p-3 rounded border border-slate-700">
      <div className="text-xs text-slate-400">{label}</div>
      <div className={`text-sm font-mono font-bold mt-0.5 ${danger ? 'text-red-400' : 'text-white'}`}>
        {value}
      </div>
    </div>
  )
}