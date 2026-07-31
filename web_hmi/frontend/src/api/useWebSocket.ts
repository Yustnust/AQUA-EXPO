import { useEffect, useRef } from 'react'
import { usePlcStore } from '../stores/plcStore'
import { useAlarmStore } from '../stores/alarmStore'

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)
  const updateUnit = usePlcStore((s) => s.updateUnit)
  const updateAlarms = useAlarmStore((s) => s.updateAlarms)

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)

        if (msg.type === 'plc_update') {
          updateUnit(msg.unit, msg.connected, msg.data)
        }

        if (msg.type === 'plc_alarm') {
          updateAlarms(msg.unit, {
            alarm_code: msg.alarm_code,
            sound_active: msg.sound_active,
            light_active: msg.light_active,
            mute_done: msg.mute_done,
            active_alarms: msg.active_alarms,
          })
        }
      } catch {
        // ignore parse errors
      }
    }

    ws.onclose = () => {
      // 自动重连
      setTimeout(() => {
        if (wsRef.current?.readyState === WebSocket.CLOSED) {
          // 触发 useEffect 重新运行
        }
      }, 3000)
    }

    return () => {
      ws.close()
    }
  }, [updateUnit, updateAlarms])
}