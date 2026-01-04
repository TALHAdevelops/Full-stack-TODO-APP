'use client'

import { Task } from '@/lib/types'
import { Button } from '@/components/ui/Button'
import { CheckCircle2, Circle, Edit2, Trash2 } from 'lucide-react'

interface TaskCardProps {
  task: Task
  onEdit: (task: Task) => void
  onDelete: (taskId: number) => void
  onToggle: (taskId: number) => void
}

export function TaskCard({ task, onEdit, onDelete, onToggle }: TaskCardProps) {
  const formattedDate = new Date(task.created_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })

  return (
    <div className={`group glass-card p-6 rounded-2xl transition-all duration-500 relative overflow-hidden ${
        task.completed ? 'opacity-40 grayscale-[0.5]' : 'hover:neon-border-blue hover:neon-glow-blue'
    }`}>
      {/* Status indicator line */}
      <div className={`absolute top-0 left-0 w-1 h-full ${task.completed ? 'bg-gray-700' : 'bg-[#00f2ff]'}`}></div>

      <div className="flex items-start gap-5">
        <button
          onClick={() => onToggle(task.id)}
          className="mt-1 transition-all duration-300 transform active:scale-75"
        >
          {task.completed ? (
            <div className="w-6 h-6 rounded-full bg-gray-800 border border-gray-600 flex items-center justify-center">
                <CheckCircle2 className="w-4 h-4 text-gray-500" />
            </div>
          ) : (
            <div className="w-6 h-6 rounded-full border-2 border-[#00f2ff]/30 group-hover:border-[#00f2ff] flex items-center justify-center transition-colors">
                <Circle className="w-4 h-4 text-transparent group-hover:text-[#00f2ff]/20" />
            </div>
          )}
        </button>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-[10px] uppercase tracking-[0.2em] font-black ${task.completed ? 'text-gray-500' : 'text-[#9d00ff]'}`}>
                {task.completed ? 'archived' : 'active-io'}
            </span>
          </div>

          <h3 className={`text-lg font-bold tracking-tight leading-tight ${
              task.completed ? 'line-through text-gray-500' : 'text-white'
          }`}>
            {task.title}
          </h3>

          {task.description && (
            <p className={`mt-2 text-sm leading-relaxed ${
                task.completed ? 'text-gray-600' : 'text-gray-400'
            }`}>
              {task.description}
            </p>
          )}

          <div className="mt-4 flex items-center gap-4">
            <div className="px-2 py-0.5 rounded bg-white/5 border border-white/5 text-[9px] uppercase font-bold tracking-widest text-gray-500">
                TS-{task.id}
            </div>
            <div className="text-[9px] uppercase font-bold tracking-widest text-[#00f2ff]/50">
                SYNCED · {formattedDate}
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-all duration-300">
          <button
            onClick={() => onEdit(task)}
            className="p-2 text-gray-400 hover:text-[#00f2ff] hover:bg-[#00f2ff]/10 rounded-lg transition-all"
            title="Update Parameters"
          >
            <Edit2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="p-2 text-gray-400 hover:text-[#ff00c8] hover:bg-[#ff00c8]/10 rounded-lg transition-all"
            title="Terminate Process"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
