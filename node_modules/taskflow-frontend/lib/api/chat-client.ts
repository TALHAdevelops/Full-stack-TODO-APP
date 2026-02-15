/**
 * Chat API client for communicating with TaskFlow Phase III chat endpoint
 * @spec: T-331 (spec.md FR-306-FR-307, plan.md API Integration)
 */

export interface ToolCallResult {
  tool_name: string
  input?: Record<string, unknown>
  result: Record<string, unknown>
}

export interface ChatResponse {
  id: string
  conversation_id: string
  user_id: string
  content: string
  tool_calls: ToolCallResult[]
  created_at: string
}

export interface ChatRequest {
  conversation_id?: string
  message: string
}

interface APIErrorResponse {
  detail: string
}

class ChatAPIError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(`Chat API Error (${status}): ${detail}`)
  }
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const REQUEST_TIMEOUT = 30000 // 30 seconds

/**
 * Send a message to the chat endpoint
 * @spec: T-331
 */
export async function sendMessage(
  userId: string,
  request: ChatRequest,
  token: string
): Promise<ChatResponse> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT)

  try {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    // Handle non-200 responses
    if (!response.ok) {
      let detail = 'Unknown error'
      try {
        const errorData: APIErrorResponse = await response.json()
        detail = errorData.detail || detail
      } catch {
        detail = `HTTP ${response.status}`
      }

      throw new ChatAPIError(response.status, detail)
    }

    const data: ChatResponse = await response.json()
    return data
  } catch (error) {
    clearTimeout(timeoutId)

    if (error instanceof ChatAPIError) {
      throw error
    }

    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      throw new ChatAPIError(0, 'Network error - check your connection')
    }

    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ChatAPIError(0, 'Request timeout - server took too long to respond')
    }

    throw new ChatAPIError(0, error instanceof Error ? error.message : 'Unknown error')
  }
}

/**
 * List all conversations for the user
 * @spec: T-327
 */
export async function listConversations(
  userId: string,
  token: string
): Promise<{ id: string; title: string; created_at: string; updated_at: string }[]> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT)

  try {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/conversations`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      let detail = 'Unknown error'
      try {
        const errorData: APIErrorResponse = await response.json()
        detail = errorData.detail || detail
      } catch {
        detail = `HTTP ${response.status}`
      }

      throw new ChatAPIError(response.status, detail)
    }

    const data = await response.json()
    return data.conversations || []
  } catch (error) {
    clearTimeout(timeoutId)

    if (error instanceof ChatAPIError) {
      throw error
    }

    throw new ChatAPIError(0, error instanceof Error ? error.message : 'Unknown error')
  }
}

/**
 * Get full conversation history
 * @spec: T-327
 */
export async function getConversation(
  userId: string,
  conversationId: string,
  token: string
): Promise<{
  id: string
  title: string
  created_at: string
  updated_at: string
  messages: Array<{
    id: string
    role: string
    content: string
    tool_calls?: Record<string, unknown>
    created_at: string
  }>
}> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT)

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/${userId}/conversations/${conversationId}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        signal: controller.signal,
      }
    )

    clearTimeout(timeoutId)

    if (!response.ok) {
      let detail = 'Unknown error'
      try {
        const errorData: APIErrorResponse = await response.json()
        detail = errorData.detail || detail
      } catch {
        detail = `HTTP ${response.status}`
      }

      throw new ChatAPIError(response.status, detail)
    }

    return await response.json()
  } catch (error) {
    clearTimeout(timeoutId)

    if (error instanceof ChatAPIError) {
      throw error
    }

    throw new ChatAPIError(0, error instanceof Error ? error.message : 'Unknown error')
  }
}

export { ChatAPIError }
