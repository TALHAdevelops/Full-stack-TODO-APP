# TaskFlow Phase III Implementation Plan - AI Chatbot

**Feature**: `5-ai-chatbot`
**Created**: 2026-01-12
**Status**: Draft
**Input**: Generate Technical Implementation Plan for Phase III: TaskFlow AI Chatbot

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    TASKFLOW PHASE III ARCHITECTURE              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  FRONTEND (Vercel)   │
│  ┌────────────────┐  │
│  │  ChatKit UI    │  │ (Next.js 16+)
│  │  - Messages    │  │ - Display conversation
│  │  - Input box   │  │ - Send messages
│  │  - History     │  │ - Show responses
│  └────────────────┘  │
└──────────────┬───────┘
               │ POST /api/{user_id}/chat
               │ { conversation_id?, message, JWT }
               │
┌──────────────▼─────────────────────────────────────────────────┐
│            BACKEND (FastAPI) - Stateless Chat Endpoint         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Chat Request Handler (routes/chat.py)                   │  │
│  │  1. Validate JWT, extract user_id                        │  │
│  │  2. Verify user_id matches path parameter                │  │
│  │  3. Fetch conversation history from DB (last 20 msgs)    │  │
│  │  4. Build message context: [system_prompt, ...history]   │  │
│  │  5. Call Agent.run(messages, tools, user_id)             │  │
│  │  6. Store user/assistant messages in DB                  │  │
│  │  7. Return response to client                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  OpenAI Agent SDK (agents.py)                            │  │
│  │  ✓ System prompt: "You manage tasks for users..."        │  │
│  │  ✓ Intent routing: understands user query                │  │
│  │  ✓ Tool selection: invokes appropriate MCP tool(s)       │  │
│  │  ✓ Response generation: natural language output          │  │
│  │  ✓ Error handling: graceful failures                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ▲                                     │
│                           │ invoke_tool(tool_name, args)        │
│                           │                                     │
│  ┌──────────────────────┴─────────────────────────────────┐    │
│  │  MCP Server (mcp_server.py) - Task Operations          │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │  Tool: add_task(user_id, title, desc?)           │  │    │
│  │  │  - Verify user_id                                │  │    │
│  │  │  - Validate input (title 1-200, desc 0-1000)     │  │    │
│  │  │  - Insert into tasks table                        │  │    │
│  │  │  - Return {task_id, title, created_at}           │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │  Tool: list_tasks(user_id, filter?)              │  │    │
│  │  │  - Verify user_id                                │  │    │
│  │  │  - Query tasks WHERE user_id=? AND filter        │  │    │
│  │  │  - Return [{id, title, completed, created_at}]   │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │  Tool: complete_task(user_id, task_id)           │  │    │
│  │  │  - Verify user_id and ownership                  │  │    │
│  │  │  - Update tasks SET completed=true               │  │    │
│  │  │  - Return {task_id, status}                      │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │  Tool: update_task(user_id, task_id, ...)        │  │    │
│  │  │  - Verify user_id and ownership                  │  │    │
│  │  │  - Update tasks SET title=?, desc=? WHERE id=?   │  │    │
│  │  │  - Return {task_id, updated_at}                  │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │  Tool: delete_task(user_id, task_id)             │  │    │
│  │  │  - Verify user_id and ownership                  │  │    │
│  │  │  - DELETE FROM tasks WHERE id=? AND user_id=?    │  │    │
│  │  │  - Return {task_id, status}                      │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  └────────────────────┬─────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                        │
                        │ SQLModel ORM
                        │ (same as Phase II)
                        ▼
        ┌───────────────────────────────┐
        │  NEON POSTGRESQL DATABASE     │
        │  ┌─────────────────────────┐  │
        │  │  conversations table     │  │
        │  │  - id (UUID, PK)        │  │
        │  │  - user_id (FK)         │  │
        │  │  - title                │  │
        │  │  - created_at/updated_at│  │
        │  └─────────────────────────┘  │
        │  ┌─────────────────────────┐  │
        │  │  messages table          │  │
        │  │  - id (UUID, PK)        │  │
        │  │  - conversation_id (FK) │  │
        │  │  - user_id (FK)         │  │
        │  │  - role (user/asst)     │  │
        │  │  - content              │  │
        │  │  - tool_calls (JSON)    │  │
        │  │  - created_at           │  │
        │  └─────────────────────────┘  │
        │  ┌─────────────────────────┐  │
        │  │  tasks table (Phase II)  │  │
        │  │  - id, user_id, title...|  │
        │  │  - completed, timestamps│  │
        │  └─────────────────────────┘  │
        │  ┌─────────────────────────┐  │
        │  │  users table (Phase II)  │  │
        │  │  - id, email, name...   │  │
        │  └─────────────────────────┘  │
        └───────────────────────────────┘
```

## Component Breakdown

### 1. Chat Endpoint (backend/routes/chat.py)

**Responsibility**: HTTP request handling, JWT validation, conversation coordination

**Technology**: FastAPI, Pydantic models, SQLModel ORM

**Key Functions**:
- `POST /api/{user_id}/chat` - Main chat endpoint
- `_validate_jwt_and_user()` - Extract and verify user_id from JWT
- `_fetch_conversation_history()` - Retrieve last 20 messages from DB
- `_build_message_context()` - Assemble messages for agent
- `_call_agent()` - Invoke OpenAI Agent SDK
- `_store_messages()` - Persist user and assistant messages
- `_handle_error()` - Graceful error responses

**Input**:
```python
{
  "conversation_id": "optional-uuid",  # Continue existing or create new
  "message": "Add buy milk"            # User message
}
```

**Output**:
```python
{
  "id": "msg-uuid",
  "conversation_id": "conv-uuid",
  "user_id": "user-uuid",
  "content": "Great! I've added...",
  "tool_calls": [...],
  "created_at": "2026-01-12T10:30:00Z"
}
```

**Key Implementation Details**:
- Validate JWT in Authorization header
- Extract user_id from JWT payload
- Verify user_id matches URL path parameter (security)
- Fetch full conversation history (max 20 messages, configurable)
- Build system message + history + new message
- Pass user_id to agent for MCP tool invocation
- Store both user and assistant messages immediately (before response)
- Handle agent errors gracefully without exposing internals
- Return response with tool_calls array for transparency

**Error Handling**:
- 401: Invalid/missing JWT
- 403: user_id mismatch
- 400: Empty message
- 404: Conversation not found
- 500: Agent error (with generic message)

---

### 2. OpenAI Agent SDK Wrapper (backend/agents.py)

**Responsibility**: Intent routing, tool selection, response generation

**Technology**: OpenAI Agents SDK (Python), gpt-4o model

**Key Functions**:
- `create_agent()` - Initialize with system prompt and tools
- `run_agent()` - Execute agent on user message with context
- `parse_intent()` - Extract user intent from message
- `select_tools()` - Determine which MCP tools to invoke

**System Prompt**:
```
You are a helpful task management assistant. Your job is to help users manage their todo list.

You have access to the following operations:
- add_task: Create a new task
- list_tasks: Show pending or completed tasks
- complete_task: Mark a task as done
- delete_task: Remove a task
- update_task: Modify a task

Always:
1. Understand the user's intent from natural language
2. Invoke the appropriate tool(s)
3. Confirm the action with a friendly response
4. Include the task ID or details for reference
5. Ask for clarification if the request is ambiguous

Natural language variations you should recognize:
- "Add/create/remember" → add_task
- "Show/list/pending" → list_tasks
- "Done/complete/finished" → complete_task
- "Delete/remove" → delete_task (ask for confirmation)
- "Change/update/rename" → update_task

For ambiguous requests, ask clarifying questions rather than guessing.
```

**Intent Recognition**:
- Analyzes user message for action keywords
- Maps to one of 6 intents: CREATE, LIST, COMPLETE, UPDATE, DELETE, CLARIFY
- Extracts task references (by ID or partial name)
- Uses conversation history for context

**Tool Invocation**:
- Agent calls MCP tools with user_id parameter
- Tools return structured responses
- Agent incorporates results into natural language response
- Includes tool_calls array for transparency

**Error Recovery**:
- Retries transient errors (timeouts) once
- Escalates persistent errors to user with friendly message
- Never exposes internal error details
- Suggests next steps (e.g., "Would you like to see your task list?")

**Response Format**:
```python
{
  "content": "Great! I've added 'buy milk' to your tasks.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "input": {"user_id": "...", "title": "buy milk"},
      "result": {"task_id": 5, "created_at": "..."}
    }
  ]
}
```

---

### 3. MCP Server - Task Operations (backend/mcp_server.py)

**Responsibility**: Task CRUD operations, validation, user isolation enforcement

**Technology**: Official MCP SDK, Python, SQLModel

**Architecture**:
- Runs as subprocess on backend (stdio communication with agent)
- Implements Model Context Protocol
- Exposes 5 tools as MCP resources
- Each tool performs validation and DB operations

**Tool Implementations**:

#### Tool: add_task
```python
async def add_task(user_id: str, title: str, description: Optional[str] = None):
    # 1. Validate user_id (don't allow empty or invalid format)
    if not user_id or len(user_id) > 255:
        raise ValueError("Invalid user_id")

    # 2. Validate inputs
    title = title.strip() if title else ""
    if not title or len(title) > 200:
        raise ValueError("Title must be 1-200 characters")

    if description and len(description) > 1000:
        raise ValueError("Description max 1000 characters")

    # 3. Create task object
    new_task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=False
    )

    # 4. Insert and commit
    db.add(new_task)
    db.commit()

    # 5. Return result
    return {
        "task_id": new_task.id,
        "user_id": user_id,
        "title": title,
        "created_at": new_task.created_at.isoformat()
    }
```

#### Tool: list_tasks
```python
async def list_tasks(user_id: str, filter: Optional[str] = None):
    # 1. Verify user_id
    if not user_id:
        raise ValueError("user_id required")

    # 2. Build query
    query = select(Task).where(Task.user_id == user_id)

    # 3. Apply filter
    if filter == "pending":
        query = query.where(Task.completed == False)
    elif filter == "completed":
        query = query.where(Task.completed == True)
    elif filter and filter != "all":
        raise ValueError("Invalid filter")

    # 4. Execute and return
    tasks = db.exec(query).all()
    return [
        {
            "id": t.id,
            "user_id": t.user_id,
            "title": t.title,
            "completed": t.completed,
            "created_at": t.created_at.isoformat()
        }
        for t in tasks
    ]
```

#### Tool: complete_task
```python
async def complete_task(user_id: str, task_id: int):
    # 1. Verify user_id and ownership
    task = db.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()

    if not task:
        raise ValueError("Task not found")

    # 2. Update completion status
    task.completed = True
    db.add(task)
    db.commit()

    # 3. Return result
    return {
        "task_id": task.id,
        "status": "completed"
    }
```

#### Tool: update_task
```python
async def update_task(user_id: str, task_id: int,
                      title: Optional[str] = None,
                      description: Optional[str] = None):
    # 1. Verify ownership
    task = db.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()

    if not task:
        raise ValueError("Task not found")

    # 2. Validate and update
    if title is not None:
        title = title.strip()
        if not title or len(title) > 200:
            raise ValueError("Title invalid")
        task.title = title

    if description is not None:
        if len(description) > 1000:
            raise ValueError("Description too long")
        task.description = description

    # 3. Commit changes
    db.add(task)
    db.commit()

    # 4. Return result
    return {
        "task_id": task.id,
        "updated_at": task.updated_at.isoformat()
    }
```

#### Tool: delete_task
```python
async def delete_task(user_id: str, task_id: int):
    # 1. Verify ownership
    task = db.exec(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    ).first()

    if not task:
        raise ValueError("Task not found")

    # 2. Delete
    db.delete(task)
    db.commit()

    # 3. Return result
    return {
        "task_id": task_id,
        "status": "deleted"
    }
```

---

### 4. Frontend Chat UI (frontend/app/chat/page.tsx)

**Responsibility**: Message display, user input, API communication

**Technology**: Next.js 16+, React, OpenAI ChatKit, TypeScript

**Components**:
- `ChatPage` - Main chat container
- `MessageList` - Displays conversation history
- `MessageInput` - User message form
- `Message` - Individual message (user/assistant)

**Key Functions**:
- `useChat()` - Hook to manage chat state
- `sendMessage()` - POST to /api/{user_id}/chat
- `loadConversation()` - Fetch conversation history
- `displayToolCalls()` - Show what agent did

**Data Flow**:
```typescript
const [messages, setMessages] = useState<Message[]>([]);
const [conversationId, setConversationId] = useState<string | null>(null);

const sendMessage = async (userMessage: string) => {
  // 1. Optimistically add user message
  setMessages(prev => [...prev, { role: "user", content: userMessage }]);

  // 2. Call API
  const response = await fetch(`/api/${userId}/chat`, {
    method: "POST",
    body: JSON.stringify({
      conversation_id: conversationId,
      message: userMessage
    })
  });

  // 3. Create conversation if new
  if (!conversationId && response.conversation_id) {
    setConversationId(response.conversation_id);
  }

  // 4. Add assistant message
  setMessages(prev => [...prev, {
    role: "assistant",
    content: response.content,
    tool_calls: response.tool_calls
  }]);
};
```

**UI Elements**:
- Conversation list sidebar (conversations per user)
- Chat history scroll (newest at bottom)
- User message input with send button
- Tool calls visualization ("Added task #5", etc.)
- Loading states (spinner while agent works)
- Error handling (display friendly error messages)

---

## Integration Points

### Frontend → Backend

**Protocol**: HTTP/REST
**Endpoint**: `POST /api/{user_id}/chat`
**Authentication**: JWT in Authorization header
**Request Format**: JSON with conversation_id (optional) and message
**Response Format**: JSON with message, tool_calls, timestamps

### Backend → Agent SDK

**Protocol**: In-process Python SDK
**Type**: Synchronous function call
**Input**: Messages list, system prompt, available tools, user_id
**Output**: Agent response with tool_calls array
**Error Handling**: Exceptions caught and converted to user-friendly messages

### Agent → MCP Server

**Protocol**: MCP (Model Context Protocol) via stdio
**Communication**: JSON-RPC over standard input/output
**Tool Invocation**: Agent requests tool execution with parameters
**Tool Response**: JSON result or error message
**Timeout**: 10 seconds per tool call

### MCP → Database

**Protocol**: SQLModel ORM (Python)
**Type**: Async database operations
**Queries**: Type-safe, parameterized (no SQL injection)
**Isolation**: Every query filters by user_id
**Error Handling**: DB exceptions logged, user gets generic error

### Database Relationships

```
users (Phase II)
  ├─ id (UUID, PK)
  ├─ email
  └─ ...

    ↓ 1:N

conversations (NEW)
  ├─ id (UUID, PK)
  ├─ user_id (FK → users.id)
  ├─ title
  └─ timestamps

    ↓ 1:N

messages (NEW)
  ├─ id (UUID, PK)
  ├─ conversation_id (FK → conversations.id)
  ├─ user_id (FK → users.id)
  ├─ role (user/assistant)
  ├─ content
  └─ tool_calls (JSON)

tasks (Phase II)
  ├─ id (int, PK)
  ├─ user_id (FK → users.id)
  ├─ title
  └─ completed
```

---

## Data Flow Diagram

### Request Phase (User → Response)

```
1. USER INPUT
   ┌─────────────────────────┐
   │ User in ChatKit: "Add   │
   │ buy milk"               │
   └────────────┬────────────┘
                │
2. CLIENT SENDS
   ┌─────────────▼────────────────────────────┐
   │ POST /api/{user_id}/chat                 │
   │ Headers: Authorization: Bearer {JWT}     │
   │ Body: {                                  │
   │   "conversation_id": "conv-123",         │
   │   "message": "Add buy milk"              │
   │ }                                        │
   └────────────┬────────────────────────────┘
                │
3. BACKEND VALIDATION
   ┌─────────────▼────────────────────────────┐
   │ Chat Endpoint validates:                 │
   │ ✓ JWT valid                              │
   │ ✓ user_id from JWT matches path param    │
   │ ✓ Message not empty, <5000 chars         │
   └────────────┬────────────────────────────┘
                │
4. FETCH HISTORY
   ┌─────────────▼────────────────────────────┐
   │ SELECT messages WHERE                    │
   │   conversation_id = 'conv-123'          │
   │   user_id = 'user-123'                  │
   │ ORDER BY created_at DESC LIMIT 20        │
   │                                          │
   │ Returns: [previous messages]             │
   └────────────┬────────────────────────────┘
                │
5. BUILD AGENT INPUT
   ┌─────────────▼────────────────────────────┐
   │ messages = [                             │
   │   {role: "system", content: prompt},     │
   │   {role: "user", content: "Hello"},      │
   │   {role: "assistant", content: "Hi"},    │
   │   {role: "user", content: "Add milk"}    │
   │ ]                                        │
   │                                          │
   │ tools = [add_task, list_tasks, ...]      │
   │ user_id = "user-123"                     │
   └────────────┬────────────────────────────┘
                │
6. INVOKE AGENT
   ┌─────────────▼────────────────────────────┐
   │ agent.run(                               │
   │   messages=messages,                     │
   │   tools=tools,                           │
   │   user_id=user_id                        │
   │ )                                        │
   │                                          │
   │ Agent:                                   │
   │ ✓ Analyzes messages                      │
   │ ✓ Detects intent: CREATE                 │
   │ ✓ Selects tool: add_task                 │
   │ ✓ Invokes MCP tool                       │
   └────────────┬────────────────────────────┘
                │
7. MCP TOOL EXECUTION
   ┌─────────────▼────────────────────────────┐
   │ Tool: add_task(                          │
   │   user_id="user-123",                    │
   │   title="buy milk"                       │
   │ )                                        │
   │                                          │
   │ Validation:                              │
   │ ✓ user_id matches                        │
   │ ✓ title length valid                     │
   │                                          │
   │ Database:                                │
   │ INSERT INTO tasks (user_id, title, ...)  │
   │ VALUES ('user-123', 'buy milk', ...)     │
   │                                          │
   │ Result: {task_id: 5, created_at: ...}    │
   └────────────┬────────────────────────────┘
                │
8. AGENT RESPONSE GENERATION
   ┌─────────────▼────────────────────────────┐
   │ Agent generates response:                │
   │ "✓ Task created: Buy milk (ID: 5)"       │
   │                                          │
   │ Includes tool_calls:                     │
   │ [{                                       │
   │   "tool": "add_task",                    │
   │   "input": {...},                        │
   │   "result": {task_id: 5, ...}            │
   │ }]                                       │
   └────────────┬────────────────────────────┘
                │
9. STORE MESSAGES
   ┌─────────────▼────────────────────────────┐
   │ Transaction:                             │
   │ INSERT INTO messages (                   │
   │   conversation_id, user_id, role,        │
   │   content, created_at                    │
   │ ) VALUES (                               │
   │   'conv-123', 'user-123', 'user',        │
   │   'Add buy milk', now()                  │
   │ )                                        │
   │                                          │
   │ INSERT INTO messages (...) VALUES (      │
   │   'conv-123', 'user-123', 'assistant',   │
   │   '✓ Task created...', now()             │
   │ )                                        │
   │                                          │
   │ COMMIT                                   │
   └────────────┬────────────────────────────┘
                │
10. RETURN RESPONSE
   ┌─────────────▼────────────────────────────┐
   │ HTTP 200 OK                              │
   │ {                                        │
   │   "id": "msg-456",                       │
   │   "conversation_id": "conv-123",         │
   │   "user_id": "user-123",                 │
   │   "content": "✓ Task created: Buy milk", │
   │   "tool_calls": [{...}],                 │
   │   "created_at": "2026-01-12T10:30:00Z"   │
   │ }                                        │
   └────────────┬────────────────────────────┘
                │
11. FRONTEND DISPLAY
   ┌─────────────▼────────────────────────────┐
   │ ChatKit UI:                              │
   │ ┌─────────────────────────────────────┐ │
   │ │ User: "Add buy milk"                │ │
   │ │                                     │ │
   │ │ Assistant: "✓ Task created: Buy     │ │
   │ │ milk (ID: 5)"                       │ │
   │ │                                     │ │
   │ │ [Tooltip: Added task via MCP tool]  │ │
   │ └─────────────────────────────────────┘ │
   └─────────────────────────────────────────┘
```

---

## Database Schema (New Tables)

### Conversation Table

**Purpose**: Group related messages into conversations

```python
# SQLModel definition
class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=500)  # Auto-generated or user-provided
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Constraints**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `user_id` → `users(id)` with CASCADE DELETE
- INDEX: `(user_id)` for fast user lookups
- NOT NULL: `id`, `user_id`, `title`, `created_at`, `updated_at`

**SQL**:
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_conversation_user_id (user_id)
);
```

---

### Message Table

**Purpose**: Store individual messages (user or assistant)

```python
# SQLModel definition
class Message(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    role: str  # "user" or "assistant"
    content: str  # Message text
    tool_calls: Optional[str] = Field(default=None)  # JSON-serialized
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Constraints**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `conversation_id` → `conversations(id)` with CASCADE DELETE
- FOREIGN KEY: `user_id` → `users(id)` with CASCADE DELETE
- INDEX: `(conversation_id, created_at)` for fast message retrieval
- INDEX: `(user_id)` for audit trail queries
- CHECK: `role IN ('user', 'assistant')`
- NOT NULL: `id`, `conversation_id`, `user_id`, `role`, `content`, `created_at`

**SQL**:
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls JSON NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_message_conversation_created (conversation_id, created_at),
    INDEX idx_message_user (user_id)
);
```

---

### Tool Calls JSON Schema

**Structure**: Array of executed tools

```typescript
interface ToolCall {
  tool_name: string;        // "add_task", "list_tasks", etc.
  input: Record<string, any>;   // Tool input parameters
  result: Record<string, any>;  // Tool output
  executed_at: string;      // ISO timestamp
  error?: string;           // Optional error message
}
```

**Example**:
```json
[
  {
    "tool_name": "add_task",
    "input": {
      "user_id": "user-123",
      "title": "buy milk"
    },
    "result": {
      "task_id": 5,
      "title": "buy milk",
      "created_at": "2026-01-12T10:30:00Z"
    },
    "executed_at": "2026-01-12T10:30:00.123Z"
  }
]
```

---

## Service Boundaries

| Service | Owns | Doesn't Own | Interface |
|---------|------|-------------|-----------|
| **Chat Endpoint** | Request routing, JWT validation, user_id verification, conversation persistence, error handling | Agent logic, tool execution, database operations | HTTP REST API |
| **Agent SDK** | Intent routing, tool selection, response generation, error recovery | Actual tool execution, database access, JWT verification | Python async functions |
| **MCP Server** | Task CRUD operations, input validation, user_id verification, database persistence | Agent logic, HTTP handling, JWT verification | MCP protocol (stdio) |
| **SQLModel ORM** | Type-safe database queries, parameterization, connection pooling | Business logic, API design, user authentication | Python data models |
| **Frontend ChatKit** | Message display, user input, API communication | Backend logic, database design, authentication | TypeScript React components |
| **Database** | Data persistence, transactions, ACID guarantees | Application logic, API design | SQL, connection pooling |

---

## Performance Considerations

### Response Time Targets

| Component | Target | Rationale |
|-----------|--------|-----------|
| Chat Endpoint (total) | <5 seconds (P95) | User expectation for conversational interface |
| History Fetch | <500ms | 20 messages from DB, indexed query |
| Agent Execution | <2 seconds | Intent routing + tool selection (minimal inference) |
| MCP Tool | <2 seconds | Database operation + validation |
| Response Persistence | <100ms | 2 inserts to messages table |
| Total Buffer | 500ms | Network latency, connection overhead |

### Optimization Strategies

**1. Conversation History Limit**
- Fetch last 20 messages (configurable)
- Reduces context size for agent
- Speeds up history retrieval (indexed query)
- Full history still available (search endpoint)

**2. Agent Model Selection**
- Use `gpt-4o` (optimized for speed/quality balance)
- Consider `gpt-4-turbo` for slower/cheaper alternative
- No long-context models needed (history kept short)

**3. MCP Tool Timeout**
- 10 seconds per tool call
- Prevents hanging on database issues
- Allows retry for transient failures

**4. Database Indexes**

| Table | Index | Reason |
|-------|-------|--------|
| conversations | (user_id) | Filter by user |
| conversations | (user_id, updated_at) | Recent conversations for user |
| messages | (conversation_id, created_at) | Get messages in order |
| messages | (user_id) | Audit trail queries |
| tasks | (user_id) | Filter by user (existing Phase II) |
| tasks | (user_id, completed) | List pending/completed tasks |

**5. Connection Pooling**
- Min connections: 10
- Max connections: 20
- Max idle time: 30 seconds
- Health check: ping every 5 minutes

**6. Caching Strategy**
- Agent system prompt: Cached (never changes)
- Conversation history: Not cached (always fresh from DB)
- Task list: Not cached (consistency more important)
- User data: Fetched once at request time

---

## Deployment Topology

### Environment Setup

```
PRODUCTION:
  Frontend (Vercel)
    ├─ Environment: BACKEND_URL=https://backend.example.com
    ├─ Environment: BETTER_AUTH_SECRET=<shared-secret>
    └─ Environment: OPENAI_API_KEY=<api-key>

  Backend (Railway/Render/Fly.io or local)
    ├─ Environment: DATABASE_URL=<neon-connection>
    ├─ Environment: BETTER_AUTH_SECRET=<shared-secret>
    ├─ Environment: FRONTEND_URL=https://frontend.example.com
    ├─ Environment: OPENAI_API_KEY=<api-key>
    └─ Environment: OPENAI_MODEL=gpt-4o

  Database (Neon)
    ├─ Two new tables: conversations, messages
    ├─ Indexes on (user_id), (conversation_id, created_at)
    └─ Connection pooling enabled
```

### Component Deployment

| Component | Platform | Scaling | Notes |
|-----------|----------|---------|-------|
| Frontend | Vercel | Automatic CDN | Next.js deployment, static + dynamic |
| Backend | Railway/Render/Fly | Manual/auto replicas | FastAPI with uvicorn |
| MCP Server | Backend process | Same as backend | Subprocess, stdio communication |
| Database | Neon | Serverless scaling | Auto-scaling, no management |
| OpenAI API | External | N/A | Rate limiting: 90k RPM (generous) |

### Network Topology

```
┌─────────────────────────────────────────┐
│  User Browser (HTTP/HTTPS)              │
└────────────┬────────────────────────────┘
             │
    ┌────────▼─────────┐
    │ Vercel CDN       │
    │ (Frontend)       │
    └────────┬─────────┘
             │ HTTPS
    ┌────────▼──────────────┐
    │ Backend Service       │
    │ (Railway/Render/Fly)  │
    │ - FastAPI app         │
    │ - MCP subprocess      │
    │ - Agent SDK           │
    └────────┬──────────────┘
             │ (connection pool)
    ┌────────▼──────────────┐
    │ Neon PostgreSQL       │
    │ (conversations, msgs) │
    └───────────────────────┘

             + (API calls)
    ┌────────────────────────┐
    │ OpenAI API (external)  │
    │ gpt-4o model           │
    └────────────────────────┘
```

---

## High-Level Sequencing

### Phase 1: Database Setup (Week 1)

**Tasks**:
1. Create Conversation table migration
2. Create Message table migration
3. Add indexes on (user_id), (conversation_id, created_at)
4. Run migrations on Neon

**Output**: New tables ready for data persistence

---

### Phase 2: Backend Core (Week 2)

**Tasks**:
1. Implement Chat Endpoint (routes/chat.py)
   - JWT validation
   - History fetching
   - Message context building
   - Error handling

2. Implement Agent Wrapper (agents.py)
   - System prompt configuration
   - Intent recognition
   - Tool selection
   - Response generation

3. Implement MCP Server (mcp_server.py)
   - Tool definitions (add_task, list_tasks, complete_task, update_task, delete_task)
   - Input validation
   - User_id verification
   - Database operations

**Output**: Backend can receive chat messages and invoke MCP tools

---

### Phase 3: Frontend UI (Week 2-3)

**Tasks**:
1. Create Chat Page (frontend/app/chat/page.tsx)
   - Message list display
   - User input form
   - API integration

2. Create Message Components
   - User message (right-aligned, light background)
   - Assistant message (left-aligned, darker)
   - Tool calls visualization

3. State Management (useChat hook)
   - Messages array
   - Conversation ID
   - Loading state
   - Error state

**Output**: Frontend can send messages and display responses

---

### Phase 4: Integration & Testing (Week 3)

**Tasks**:
1. End-to-end testing
   - User adds task via chat
   - Task appears in both chat and task list
   - Conversation history persists
   - User isolation verified

2. Performance testing
   - Response time <5 seconds (P95)
   - Tool execution <2 seconds
   - Agent decision <1 second

3. Security testing
   - JWT validation
   - User isolation
   - SQL injection prevention
   - XSS prevention

4. Error handling testing
   - Network errors
   - Tool failures
   - Agent errors
   - Database errors

**Output**: All tests passing, ready for production

---

### Phase 5: Deployment (Week 4)

**Tasks**:
1. Production environment setup
2. Deploy frontend to Vercel
3. Deploy backend to Railway/Render/Fly
4. Configure DNS and CORS
5. Monitor and iterate

**Output**: Live Phase III chatbot interface

---

## Implementation Phases Detail

### Phase 1: Database Initialization

**Migration 1: Create Conversations Table**
```python
# alembic/versions/xxx_create_conversations.py
def upgrade():
    op.create_table(
        'conversation',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('user_id', GUID(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversation_user_id', 'conversation', ['user_id'])
```

**Migration 2: Create Messages Table**
```python
# alembic/versions/xxx_create_messages.py
def upgrade():
    op.create_table(
        'message',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('conversation_id', GUID(), nullable=False),
        sa.Column('user_id', GUID(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("role IN ('user', 'assistant')")
    )
    op.create_index('idx_message_conversation_created', 'message', ['conversation_id', 'created_at'])
    op.create_index('idx_message_user', 'message', ['user_id'])
```

---

### Phase 2: Backend Implementation Sequence

**Step 1: Chat Endpoint Core**
- Request validation (JWT, user_id)
- History fetching
- Error handling framework

**Step 2: Agent Integration**
- OpenAI SDK initialization
- System prompt configuration
- Basic intent recognition

**Step 3: MCP Tool Development**
- add_task implementation
- list_tasks implementation
- complete_task, update_task, delete_task

**Step 4: Message Persistence**
- User message storage
- Assistant message storage
- Transaction handling

**Step 5: Error Recovery**
- Graceful error handling
- Retry logic for transient failures
- User-friendly error messages

---

### Phase 3: Frontend Implementation Sequence

**Step 1: Basic Layout**
- Chat container
- Message display area
- Input form

**Step 2: Message Components**
- User message rendering
- Assistant message rendering
- Tool calls visualization

**Step 3: API Integration**
- useChat hook
- Message sending
- History loading

**Step 4: State Management**
- Conversation tracking
- Loading states
- Error states

**Step 5: UX Polish**
- Auto-scroll to latest message
- Typing indicators
- Empty state messaging

---

## Dependencies & Prerequisites

**Backend**:
- OpenAI Agents SDK (Python)
- Official MCP SDK (Python)
- fastapi >= 0.100
- sqlmodel >= 0.0.14
- pydantic >= 2.0
- python-jose >= 3.3

**Frontend**:
- next >= 14.0
- react >= 18
- @openai/chat-kit >= latest
- typescript >= 5.0

**Infrastructure**:
- Neon PostgreSQL (existing)
- Better Auth (existing)
- OpenAI API key (new)
- Railway/Render/Fly.io account (existing)

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| OpenAI API rate limits | High | Implement backoff strategy, cache system prompt |
| Agent hallucinating | Medium | Clear system prompt, validate tool results |
| MCP tool crashes | High | Process restart, timeout handling, fallback |
| Database connection loss | High | Connection retry, circuit breaker, user feedback |
| User isolation breach | Critical | Test thoroughly, code review, audit logging |
| Performance degradation | Medium | Monitor response times, scale backend |

