import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import OverviewPage from './pages/OverviewPage'
import UnitDetailPage from './pages/UnitDetailPage'
import ManualControlPage from './pages/ManualControlPage'
import ParamSettingsPage from './pages/ParamSettingsPage'
import AlarmLogPage from './pages/AlarmLogPage'
import TrendPage from './pages/TrendPage'
import CommStatusPage from './pages/CommStatusPage'
import SystemSettingsPage from './pages/SystemSettingsPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />
        } />
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<OverviewPage />} />
          <Route path="unit/:unitId" element={<UnitDetailPage />} />
          <Route path="manual" element={<ManualControlPage />} />
          <Route path="params" element={<ParamSettingsPage />} />
          <Route path="alarms" element={<AlarmLogPage />} />
          <Route path="trend" element={<TrendPage />} />
          <Route path="comm" element={<CommStatusPage />} />
          <Route path="settings" element={<SystemSettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}