import { create } from 'zustand'

interface PlcUnitData {
  connected: boolean
  data: Record<string, unknown>
}

interface PlcState {
  units: Record<number, PlcUnitData>
  updateUnit: (unitId: number, connected: boolean, data: Record<string, unknown>) => void
  getUnit: (unitId: number) => PlcUnitData | undefined
}

export const usePlcStore = create<PlcState>((set, get) => ({
  units: {},
  updateUnit: (unitId, connected, data) =>
    set((state) => ({
      units: {
        ...state.units,
        [unitId]: { connected, data },
      },
    })),
  getUnit: (unitId) => get().units[unitId],
}))