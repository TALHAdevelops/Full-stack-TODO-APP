export interface User {
  id: string
  email: string
  name?: string
  token?: string
  created_at: string
}

export interface Task {
  id: number
  user_id: string
  title: string
  description: string
  completed: boolean
  created_at: string
  updated_at: string
  due_date?: string | null
  recurrence_rule?: string | null
  is_recurring?: boolean
  next_occurrence?: string | null
}

export interface ApiError {
  detail: string | Record<string, string>
}

export interface TaskCreateData {
  title: string
  description?: string
  due_date?: string
  recurrence_rule?: string
}

export interface TaskUpdateData {
  title?: string
  description?: string
}

// Phase 5: WebSocket event types
export interface TaskWSMessage {
  type: string
  data: Record<string, unknown>
  timestamp: string
  correlation_id: string
  event_id: string
}

export type WSConnectionState = "connecting" | "connected" | "disconnected" | "reconnecting"

export interface ReminderCreateData {
  remind_at: string
}
