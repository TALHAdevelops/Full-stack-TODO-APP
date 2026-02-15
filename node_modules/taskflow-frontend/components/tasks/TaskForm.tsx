'use client'

import { useState, useEffect } from 'react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Task } from '@/lib/types'

interface TaskFormProps {
  onSubmit: (title: string, description: string) => Promise<void>
  onCancel?: () => void
  initialTask?: Task
  loading?: boolean
}

import { Terminal, Plus, Save, X } from 'lucide-react'

export function TaskForm({ onSubmit, onCancel, initialTask, loading }: TaskFormProps) {
  const [title, setTitle] = useState(initialTask?.title || '')
  const [description, setDescription] = useState(initialTask?.description || '')
  const [error, setError] = useState('')

  useEffect(() => {
    if (initialTask) {
      setTitle(initialTask.title)
      setDescription(initialTask.description || '')
    }
  }, [initialTask])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) {
      setError('System Error: Title Required')
      return
    }
    setError('')
    await onSubmit(title, description)
    if (!initialTask) {
      setTitle('')
      setDescription('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className={`glass-card p-8 rounded-2xl border-white/5 space-y-6 relative overflow-hidden ${initialTask ? 'neon-border-purple neon-glow-purple' : ''}`}>
      <div className="flex items-center gap-3 mb-2">
        <div className={`p-2 rounded bg-white/5 border border-white/10 ${initialTask ? 'text-[#9d00ff]' : 'text-[#00f2ff]'}`}>
            <Terminal className="w-5 h-5" />
        </div>
        <h3 className="text-sm font-black text-white uppercase tracking-[0.3em]">
          {initialTask ? 'Modify Parameters' : 'New Command'}
        </h3>
      </div>

      <div className="space-y-4">
        <Input
          label="Objective"
          value={title}
          onChange={setTitle}
          placeholder="ENTER TASK TITLE..."
          required
          maxLength={200}
          error={error}
        />

        <Input
          label="Data Parameters"
          type="textarea"
          value={description}
          onChange={setDescription}
          placeholder="ADDITIONAL SYSTEM LOGS..."
          maxLength={1000}
        />
      </div>

      <div className="flex gap-4 justify-end pt-4">
        {onCancel && (
          <Button variant="ghost" onClick={onCancel} disabled={loading} className="gap-2">
            <X className="w-4 h-4" />
            Abort
          </Button>
        )}
        <Button type="submit" variant={initialTask ? 'secondary' : 'primary'} loading={loading} className="gap-2 px-10">
          {initialTask ? (
            <>
              <Save className="w-4 h-4" />
              Commit Changes
            </>
          ) : (
            <>
              <Plus className="w-4 h-4" />
              Execute Task
            </>
          )}
        </Button>
      </div>
    </form>
  )
}
