import { create } from 'zustand'

interface AuthState {
  token: string | null
  username: string | null
  role: string | null
  passwordChanged: boolean
  isAuthenticated: boolean
  login: (token: string, username: string, role: string, passwordChanged: boolean) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  username: localStorage.getItem('username'),
  role: localStorage.getItem('role'),
  passwordChanged: localStorage.getItem('passwordChanged') === 'true',
  isAuthenticated: !!localStorage.getItem('token'),
  login: (token, username, role, passwordChanged) => {
    localStorage.setItem('token', token)
    localStorage.setItem('username', username)
    localStorage.setItem('role', role)
    localStorage.setItem('passwordChanged', String(passwordChanged))
    set({ token, username, role, passwordChanged, isAuthenticated: true })
  },
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
    localStorage.removeItem('passwordChanged')
    set({ token: null, username: null, role: null, passwordChanged: false, isAuthenticated: false })
  },
}))