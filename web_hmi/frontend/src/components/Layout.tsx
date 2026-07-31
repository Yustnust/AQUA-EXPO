import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useWebSocket } from '../api/useWebSocket'
import AlarmBanner from './AlarmBanner'
import AlarmPopup from './AlarmPopup'

const NAV_ITEMS = [
  { path: '/', label: '总览', icon: '□' },
  { path: '/manual', label: '手动控制', icon: '⚙' },
  { path: '/params', label: '参数设置', icon: '📐' },
  { path: '/alarms', label: '报警日志', icon: '⚠' },
  { path: '/trend', label: '趋势曲线', icon: '📈' },
  { path: '/comm', label: '通讯维护', icon: '🔗' },
  { path: '/settings', label: '系统设置', icon: '🔧' },
]

export default function Layout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { username, role, logout } = useAuthStore()

  // 连接 WebSocket
  useWebSocket()

  return (
    <div className="flex h-screen overflow-hidden">
      {/* 侧边栏 */}
      <aside className="w-48 bg-slate-800 flex flex-col shrink-0">
        <div className="p-3 border-b border-slate-700">
          <h1 className="text-sm font-bold text-blue-400">AQUA-EXPO</h1>
          <p className="text-xs text-slate-400 mt-0.5">药液配置与加注</p>
        </div>
        <nav className="flex-1 py-2">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path ||
              (item.path === '/' && location.pathname.startsWith('/unit/'))
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full text-left px-4 py-2.5 text-sm flex items-center gap-2 transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-700'
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>
        <div className="p-3 border-t border-slate-700">
          <div className="text-xs text-slate-400">
            <span className="text-slate-300">{username}</span>
            <span className={`ml-2 px-1.5 py-0.5 rounded text-xs ${
              role === 'admin' ? 'bg-red-800 text-red-200' : 'bg-blue-800 text-blue-200'
            }`}>
              {role === 'admin' ? '管理员' : '操作员'}
            </span>
          </div>
          <button
            onClick={logout}
            className="mt-2 text-xs text-slate-500 hover:text-slate-300"
          >
            退出登录
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <AlarmBanner />
        <div className="flex-1 overflow-auto p-4">
          <Outlet />
        </div>
      </main>

      {/* 报警强制弹窗 */}
      <AlarmPopup />
    </div>
  )
}