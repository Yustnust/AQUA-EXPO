import { useState } from 'react'

interface ConfirmDialogProps {
  title: string
  message: string
  onConfirm: () => void | Promise<void>
  onCancel: () => void
  confirmText?: string
  danger?: boolean
}

export default function ConfirmDialog({
  title,
  message,
  onConfirm,
  onCancel,
  confirmText = '确认',
  danger = false,
}: ConfirmDialogProps) {
  const [loading, setLoading] = useState(false)

  const handleConfirm = async () => {
    setLoading(true)
    try {
      await onConfirm()
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="alarm-overlay" onClick={onCancel}>
      <div
        className="bg-slate-800 border border-slate-600 rounded-lg p-6 max-w-md w-full shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
        <p className="text-sm text-slate-300 mb-4">{message}</p>
        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-slate-600 hover:bg-slate-500 rounded text-white text-sm"
            disabled={loading}
          >
            取消
          </button>
          <button
            onClick={handleConfirm}
            className={`px-4 py-2 rounded text-white text-sm font-bold ${
              danger
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
            disabled={loading}
          >
            {loading ? '执行中...' : confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}