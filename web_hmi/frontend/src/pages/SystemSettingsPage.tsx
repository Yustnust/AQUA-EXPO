import { useState, useEffect } from 'react'
import { useAuthStore } from '../stores/authStore'
import { authApi } from '../api/client'
import ConfirmDialog from '../components/ConfirmDialog'

interface UserInfo {
  username: string
  role: string
  password_changed: boolean
}

export default function SystemSettingsPage() {
  const { username, role } = useAuthStore()
  const [users, setUsers] = useState<UserInfo[]>([])
  const [showChangePwd, setShowChangePwd] = useState(false)
  const [oldPwd, setOldPwd] = useState('')
  const [newPwd, setNewPwd] = useState('')
  const [showCreateUser, setShowCreateUser] = useState(false)
  const [newUsername, setNewUsername] = useState('')
  const [newUserPwd, setNewUserPwd] = useState('')
  const [newUserRole, setNewUserRole] = useState('operator')
  const [deleteUser, setDeleteUser] = useState<string | null>(null)

  const loadUsers = async () => {
    if (role !== 'admin') return
    try {
      const res = await authApi.getUsers()
      setUsers(res)
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    loadUsers()
  }, [role])

  const handleChangePassword = async () => {
    try {
      await authApi.changePassword(oldPwd, newPwd)
      alert('密码修改成功')
      setShowChangePwd(false)
      setOldPwd('')
      setNewPwd('')
    } catch (err) {
      alert(err instanceof Error ? err.message : '修改失败')
    }
  }

  const handleCreateUser = async () => {
    try {
      await authApi.createUser(newUsername, newUserPwd, newUserRole)
      alert('用户创建成功')
      setShowCreateUser(false)
      setNewUsername('')
      setNewUserPwd('')
      loadUsers()
    } catch (err) {
      alert(err instanceof Error ? err.message : '创建失败')
    }
  }

  const handleDeleteUser = async () => {
    if (!deleteUser) return
    try {
      await authApi.deleteUser(deleteUser)
      setDeleteUser(null)
      loadUsers()
    } catch (err) {
      alert(err instanceof Error ? err.message : '删除失败')
    }
  }

  return (
    <div>
      <h2 className="text-lg font-bold text-white mb-4">系统设置</h2>

      {/* 修改密码 */}
      <div className="bg-slate-800 rounded border border-slate-700 p-4 mb-4">
        <h3 className="text-sm font-bold text-white mb-3">账户安全</h3>
        <div className="text-xs text-slate-400 mb-2">
          当前用户: {username} ({role === 'admin' ? '管理员' : '操作员'})
        </div>
        {!showChangePwd ? (
          <button
            onClick={() => setShowChangePwd(true)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm"
          >
            修改密码
          </button>
        ) : (
          <div className="space-y-3">
            <input
              type="password"
              value={oldPwd}
              onChange={(e) => setOldPwd(e.target.value)}
              placeholder="当前密码"
              className="w-full px-3 py-1.5 bg-slate-700 border border-slate-600 rounded text-white text-sm"
            />
            <input
              type="password"
              value={newPwd}
              onChange={(e) => setNewPwd(e.target.value)}
              placeholder="新密码"
              className="w-full px-3 py-1.5 bg-slate-700 border border-slate-600 rounded text-white text-sm"
            />
            <div className="flex gap-2">
              <button
                onClick={handleChangePassword}
                className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm"
              >
                确认
              </button>
              <button
                onClick={() => setShowChangePwd(false)}
                className="px-4 py-1.5 bg-slate-600 hover:bg-slate-500 rounded text-white text-sm"
              >
                取消
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 用户管理（仅管理员） */}
      {role === 'admin' && (
        <div className="bg-slate-800 rounded border border-slate-700 p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-white">用户管理</h3>
            <button
              onClick={() => setShowCreateUser(true)}
              className="px-3 py-1.5 bg-green-600 hover:bg-green-700 rounded text-white text-xs"
            >
              新建用户
            </button>
          </div>

          {showCreateUser && (
            <div className="mb-4 p-3 bg-slate-700 rounded space-y-2">
              <input
                type="text"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                placeholder="用户名"
                className="w-full px-3 py-1.5 bg-slate-600 border border-slate-500 rounded text-white text-sm"
              />
              <input
                type="password"
                value={newUserPwd}
                onChange={(e) => setNewUserPwd(e.target.value)}
                placeholder="密码"
                className="w-full px-3 py-1.5 bg-slate-600 border border-slate-500 rounded text-white text-sm"
              />
              <select
                value={newUserRole}
                onChange={(e) => setNewUserRole(e.target.value)}
                className="w-full px-3 py-1.5 bg-slate-600 border border-slate-500 rounded text-white text-sm"
              >
                <option value="operator">操作员</option>
                <option value="admin">管理员</option>
              </select>
              <div className="flex gap-2">
                <button onClick={handleCreateUser} className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-white text-xs">创建</button>
                <button onClick={() => setShowCreateUser(false)} className="px-3 py-1 bg-slate-500 hover:bg-slate-400 rounded text-white text-xs">取消</button>
              </div>
            </div>
          )}

          <table className="w-full text-sm">
            <thead className="bg-slate-700">
              <tr>
                <th className="text-left px-3 py-1.5 text-slate-300">用户名</th>
                <th className="text-left px-3 py-1.5 text-slate-300">角色</th>
                <th className="text-left px-3 py-1.5 text-slate-300">密码状态</th>
                <th className="px-3 py-1.5"></th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.username} className="border-t border-slate-700">
                  <td className="px-3 py-1.5 text-white">{u.username}</td>
                  <td className="px-3 py-1.5">
                    <span className={`px-1.5 py-0.5 rounded text-xs ${
                      u.role === 'admin' ? 'bg-red-800 text-red-200' : 'bg-blue-800 text-blue-200'
                    }`}>
                      {u.role === 'admin' ? '管理员' : '操作员'}
                    </span>
                  </td>
                  <td className="px-3 py-1.5 text-slate-400">
                    {u.password_changed ? '已修改' : '默认密码'}
                  </td>
                  <td className="px-3 py-1.5">
                    {u.username !== username && (
                      <button
                        onClick={() => setDeleteUser(u.username)}
                        className="px-2 py-0.5 bg-red-700 hover:bg-red-600 rounded text-white text-xs"
                      >
                        删除
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {deleteUser && (
        <ConfirmDialog
          title="确认删除用户"
          message={`确认删除用户 ${deleteUser}？此操作不可撤销。`}
          onConfirm={handleDeleteUser}
          onCancel={() => setDeleteUser(null)}
          confirmText="确认删除"
          danger
        />
      )}
    </div>
  )
}