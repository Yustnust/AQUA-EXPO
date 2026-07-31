import { create } from 'zustand'

interface AlarmItem {
  bit_index: number
  symbol: string
  alarm_code: number
  level: string
  color: string
  forced_ack: boolean
  text: string
}

interface AlarmState {
  unitAlarms: Record<number, {
    alarm_code: number
    sound_active: boolean
    light_active: boolean
    mute_done: boolean
    active_alarms: AlarmItem[]
  }>
  showPopup: boolean
  popupUnit: number | null
  updateAlarms: (unitId: number, data: {
    alarm_code: number
    sound_active: boolean
    light_active: boolean
    mute_done: boolean
    active_alarms: AlarmItem[]
  }) => void
  acknowledgePopup: () => void
}

export const useAlarmStore = create<AlarmState>((set) => ({
  unitAlarms: {},
  showPopup: false,
  popupUnit: null,
  updateAlarms: (unitId, data) =>
    set((state) => {
      const prev = state.unitAlarms[unitId]
      const prevCount = prev?.active_alarms.length ?? 0
      const newCount = data.active_alarms.length
      // 新报警触发强制弹窗
      const hasNewAlarm = newCount > prevCount && data.active_alarms.some(
        (a) => !prev?.active_alarms.find((p) => p.bit_index === a.bit_index)
      )
      return {
        unitAlarms: {
          ...state.unitAlarms,
          [unitId]: data,
        },
        showPopup: hasNewAlarm ? true : state.showPopup,
        popupUnit: hasNewAlarm ? unitId : state.popupUnit,
      }
    }),
  acknowledgePopup: () => set({ showPopup: false, popupUnit: null }),
}))