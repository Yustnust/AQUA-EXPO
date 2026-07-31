const BASE_URL = '/api/v1'

function getToken(): string | null {
  return localStorage.getItem('token')
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  })

  if (res.status === 401) {
    localStorage.clear()
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail || `HTTP ${res.status}`)
  }

  return res.json()
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string) =>
    request<T>(path, { method: 'DELETE' }),
}

// Auth API
export const authApi = {
  login: (username: string, password: string) =>
    api.post<{
      access_token: string
      username: string
      role: string
      password_changed: boolean
    }>('/auth/login', { username, password }),
  me: () => api.get<{ username: string; role: string; password_changed: boolean }>('/auth/me'),
  changePassword: (oldPassword: string, newPassword: string) =>
    api.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword }),
  getUsers: () => api.get<Array<{ username: string; role: string; password_changed: boolean }>>('/auth/users'),
  createUser: (username: string, password: string, role: string) =>
    api.post('/auth/users', { username, password, role }),
  deleteUser: (username: string) => api.delete(`/auth/users/${username}`),
}

// PLC API
export const plcApi = {
  getStatus: () => api.get<{ units: Array<{ unit: number; connected: boolean; host: string; port: number }> }>('/plc/status'),
  getData: () => api.get<{ timestamp: string; units: Record<string, { connected: boolean; data: Record<string, unknown> }> }>('/plc/data'),
  getUnitData: (unitId: number) => api.get<{ unit: number; connected: boolean; data: Record<string, unknown> }>(`/plc/data/${unitId}`),
  getVariables: () => api.get<Array<{ name: string; v_addr: number; dtype: string; writable: boolean; note: string }>>('/plc/variables'),
  write: (unit: number, name: string, value: unknown) =>
    api.post('/plc/write', { unit, name, value }),
  writePulse: (unit: number, name: string, duration?: number) =>
    api.post('/plc/write-pulse', { unit, name, duration: duration ?? 0.5 }),
}

// History API
export const historyApi = {
  getVariables: () => api.get<Array<{ name: string; note: string; dtype: string; group: string }>>('/history/variables'),
  query: (unitId: number, vars?: string[], start?: string, end?: string, minutes?: number) => {
    const params = new URLSearchParams()
    if (vars?.length) params.set('vars', vars.join(','))
    if (start) params.set('start', start)
    if (end) params.set('end', end)
    if (minutes) params.set('minutes', String(minutes))
    return api.get<{ unit: number; start: string; end: string; variables: string[]; data: Record<string, Array<{ ts: string; value: number }>> }>(`/history/query/${unitId}?${params}`)
  },
  getRetention: () => api.get<{ retention_days: number }>('/history/retention'),
  setRetention: (days: number) => api.post('/history/retention', { days }),
}

// Alarm API
export const alarmApi = {
  getDefinitions: () => api.get<Array<{ bit_index: number; symbol: string; alarm_code: number; level: string; color: string; forced_ack: boolean; text: string }>>('/alarm/definitions'),
  getActive: (unitId?: number) => {
    if (unitId) return api.get<{ unit: number; active_alarms: unknown[] }>(`/alarm/active/${unitId}`)
    return api.get<{ active_alarms: Record<string, unknown[]> }>('/alarm/active')
  },
  getEvents: (params?: { unit_id?: number; level?: string; action?: string; minutes?: number; limit?: number }) => {
    const qs = new URLSearchParams()
    if (params?.unit_id) qs.set('unit_id', String(params.unit_id))
    if (params?.level) qs.set('level', params.level)
    if (params?.action) qs.set('action', params.action)
    if (params?.minutes) qs.set('minutes', String(params.minutes))
    if (params?.limit) qs.set('limit', String(params.limit))
    return api.get<{ start: string; end: string; count: number; events: Array<Record<string, unknown>> }>(`/alarm/events?${qs}`)
  },
}