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
}

export interface ApiError {
  detail: string | Record<string, string>
}

export interface TaskCreateData {
  title: string
  description?: string
}

export interface TaskUpdateData {
  title?: string
  description?: string
}
