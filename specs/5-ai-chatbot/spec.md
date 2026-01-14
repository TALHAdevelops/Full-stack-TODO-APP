# Feature Specification: TaskFlow Phase III - AI Chatbot

**Feature Branch**: `5-ai-chatbot`
**Created**: 2026-01-12
**Status**: Draft
**Input**: Generate detailed Feature Specification for Phase III: TaskFlow AI Chatbot with conversational interface via MCP tools

## User Scenarios & Testing

### User Story 1 - Add Task via Natural Language (Priority: P1)

User wants to quickly add a task by typing a natural language message like "Add buy milk" or "Remember to call the plumber tomorrow" instead of using a form. The chatbot understands the intent and creates the task.

**Why this priority**: Core MVP feature. Task creation is the fundamental operation users repeat most frequently. Natural language input is the primary value proposition of the chatbot interface.

**Independent Test**: Can be fully tested by: user sends "Add buy milk" → agent creates task → task appears in task list. Delivers immediate task creation value without depending on other chat features.

**Acceptance Scenarios**:

1. **Given** user is authenticated and in a conversation, **When** user types "Add buy milk", **Then** agent creates a task titled "buy milk" and responds with confirmation including task ID
2. **Given** user is authenticated, **When** user types "Remember to call the plumber tomorrow", **Then** agent creates a task titled "call the plumber tomorrow" and confirms creation
3. **Given** user is authenticated, **When** user types "Create task: finish report by Friday", **Then** agent creates task with title "finish report by Friday" and confirms
4. **Given** user sends a message with multiple action words like "Add milk AND bread", **Then** agent asks for clarification: "Should I create one task 'milk AND bread' or two separate tasks?"

---

### User Story 2 - List Tasks via Chat (Priority: P1)

User wants to see their pending tasks by asking the chatbot "Show pending tasks", "What's on my list?", or similar natural language queries instead of navigating to a tasks page.

**Why this priority**: P1 - Core read operation. Users need to view tasks frequently to understand their workload. Demonstrates data retrieval through natural conversation.

**Independent Test**: Can be fully tested by: user sends "Show pending tasks" → agent retrieves user's incomplete tasks → agent displays formatted list. Works independently from other features.

**Acceptance Scenarios**:

1. **Given** user has 3 pending tasks, **When** user types "Show pending tasks", **Then** agent lists all 3 tasks with IDs, titles, and creation dates
2. **Given** user has 0 pending tasks, **When** user types "What do I need to do?", **Then** agent responds "You have no pending tasks. Great job!"
3. **Given** user types "List all tasks", **When** agent processes request, **Then** only user's own tasks are returned (not other users' tasks)
4. **Given** user types "Show completed tasks", **Then** agent asks "Do you want to see only completed tasks or all tasks?" (handles ambiguous intent)

---

### User Story 3 - Complete Task via Chat (Priority: P1)

User wants to mark a task as complete by saying "Mark task 1 done" or "Complete the milk task" instead of clicking a checkbox on the web interface.

**Why this priority**: P1 - Core state change. Task completion is primary user workflow. Demonstrates successful state mutation through conversation.

**Independent Test**: Can be fully tested by: user sends "Mark task 1 done" → agent updates task completion status → task now appears in completed list. Independent operation.

**Acceptance Scenarios**:

1. **Given** user has task ID 1 "buy milk", **When** user types "Mark task 1 done", **Then** agent marks task as complete and confirms "Task 1 is now complete"
2. **Given** user has task "buy milk", **When** user types "Complete the milk task", **Then** agent finds task by title and marks complete
3. **Given** task ID 1 is already completed, **When** user types "Mark task 1 done", **Then** agent responds "Task 1 is already marked complete" without error
4. **Given** user types "Done" with no task reference, **When** agent processes, **Then** agent asks "Which task should I mark complete? Please specify the task ID or name"

---

### User Story 4 - Update Task via Chat (Priority: P2)

User wants to modify a task description by saying "Change task 1 to 'Buy milk and bread'" or "Update the grocery list task with more details" instead of using an edit form.

**Why this priority**: P2 - Important refinement feature. Users frequently need to update task details after creation. Less critical than basic CRUD but essential for real workflows.

**Independent Test**: Can be fully tested by: user sends "Change task 1 to 'buy milk and bread'" → agent updates task title → task reflects changes in list.

**Acceptance Scenarios**:

1. **Given** task ID 1 is titled "buy milk", **When** user types "Change task 1 to 'buy milk and bread'", **Then** agent updates title and confirms "Task 1 updated: 'buy milk and bread'"
2. **Given** user types "Update task 2 description to 'high priority'", **When** agent processes, **Then** agent either updates the task or clarifies if they mean add a description field
3. **Given** user provides partial info like "Update that task", **When** agent receives ambiguous reference, **Then** agent asks "Which task? Please provide task ID or full task name"
4. **Given** user updates a task, **When** update completes, **Then** conversation history shows the change made and confirms success

---

### User Story 5 - Delete Task via Chat (Priority: P2)

User wants to remove a task by saying "Delete task 2" or "Remove the old task about filing taxes" instead of using a delete button on the web interface.

**Why this priority**: P2 - Important destructive operation. Users need to clean up their task lists. Requires careful handling to prevent accidental deletions.

**Independent Test**: Can be fully tested by: user sends "Delete task 2" → agent asks confirmation → user confirms → task is removed from list.

**Acceptance Scenarios**:

1. **Given** user has task ID 2, **When** user types "Delete task 2", **Then** agent asks "Are you sure? This will permanently remove task 2"
2. **Given** user confirmed deletion, **When** they respond "Yes", **Then** agent deletes task and confirms "Task 2 has been deleted"
3. **Given** user responds "No" to deletion confirmation, **When** agent receives response, **Then** task is preserved and agent responds "Task 2 not deleted"
4. **Given** task ID 999 doesn't exist, **When** user types "Delete task 999", **Then** agent responds "Task 999 not found"

---

### User Story 6 - Handle Ambiguous Input Gracefully (Priority: P2)

User provides unclear or multi-intent messages like "Add milk and complete the shopping list" and agent asks clarifying questions instead of failing or making wrong assumptions.

**Why this priority**: P2 - UX quality. Users naturally speak in ambiguous ways. Agent needs to handle gracefully to feel intelligent and helpful without frustrating users.

**Independent Test**: Can be fully tested by: user sends ambiguous message → agent asks clarification → user provides clarification → agent completes correct action.

**Acceptance Scenarios**:

1. **Given** user types "Add milk and complete the list", **When** agent detects multiple intents, **Then** agent asks "Do you want to: (1) create a task 'milk and complete the list', or (2) add a task and complete another task?"
2. **Given** user types "Update it", **When** no previous task context exists, **Then** agent asks "Which task would you like to update? Please provide task ID or name"
3. **Given** user types "Show me", **When** intent is unclear, **Then** agent asks "Would you like to see your pending tasks, completed tasks, or all tasks?"
4. **Given** user provides feedback "That's not what I meant", **When** agent receives correction, **Then** agent acknowledges and asks user to rephrase

---

### Edge Cases

- What happens when user references a task by partial name ("the milk one") that matches multiple tasks? → Agent asks which specific task
- How does system handle when user sends very long task title (>200 chars)? → Agent truncates to 200 chars and asks for confirmation
- What if agent tool fails (network error, DB error)? → Agent responds "Sorry, I couldn't complete that action. Please try again" without exposing technical details
- What if user is deleted but session is still active? → Subsequent chat requests fail with "Your account has been deleted"
- What if conversation history gets very long (1000+ messages)? → Agent includes only recent context (last 50 messages) to maintain performance

---

## Requirements

### Functional Requirements

**Chat Endpoint & Authentication**

- **FR-301**: System MUST provide a POST /api/{user_id}/chat endpoint that accepts authenticated requests
- **FR-302**: System MUST require valid JWT token in Authorization header for all chat requests
- **FR-303**: System MUST validate that JWT user_id matches the URL path user_id before processing chat
- **FR-304**: System MUST reject requests with 401 Unauthorized if JWT is invalid or missing
- **FR-305**: System MUST reject requests with 403 Forbidden if user_id in token doesn't match path parameter

**Chat Request/Response Contract**

- **FR-306**: Chat endpoint MUST accept request body: { conversation_id?: string, message: string }
- **FR-307**: Chat endpoint MUST return response body: { id: string, conversation_id: string, user_id: string, content: string, tool_calls: array, created_at: string }
- **FR-308**: System MUST return 400 Bad Request if message field is empty or missing
- **FR-309**: System MUST return 400 Bad Request if message exceeds 5000 characters
- **FR-310**: System MUST create new Conversation record if conversation_id not provided
- **FR-311**: System MUST validate that conversation_id belongs to authenticated user before processing

**Conversation Persistence**

- **FR-312**: System MUST store each user message as a Message record with role="user"
- **FR-313**: System MUST store each agent response as a Message record with role="assistant"
- **FR-314**: System MUST record message creation timestamp automatically
- **FR-315**: System MUST fetch full conversation history from DB on each chat request (no server-side session memory)
- **FR-316**: System MUST include conversation history in agent context for multi-turn understanding
- **FR-317**: System MUST return 404 Not Found if conversation_id doesn't exist for user

**Agent Behavior & Intent Routing**

- **FR-318**: Agent MUST understand natural language variations for task creation ("add", "create", "remember", "don't forget")
- **FR-319**: Agent MUST understand natural language variations for task listing ("show", "list", "what's pending", "what do I need")
- **FR-320**: Agent MUST understand natural language variations for task completion ("done", "complete", "finished", "mark complete")
- **FR-321**: Agent MUST understand natural language variations for task deletion ("delete", "remove", "get rid of")
- **FR-322**: Agent MUST understand natural language variations for task updates ("change", "update", "rename", "modify")
- **FR-323**: Agent MUST ask for clarification when user intent is ambiguous (multiple interpretations)
- **FR-324**: Agent MUST confirm destructive actions (delete) before executing
- **FR-325**: Agent MUST provide natural, conversational responses (not robotic)
- **FR-326**: Agent MUST include tool execution results in response (what action was taken)

**MCP Tool Implementation**

- **FR-327**: System MUST expose add_task MCP tool: add_task(user_id: string, title: string, description?: string) → {task_id, title, created_at}
- **FR-328**: System MUST expose list_tasks MCP tool: list_tasks(user_id: string, filter?: string) → [{id, title, completed, created_at}]
- **FR-329**: System MUST expose complete_task MCP tool: complete_task(user_id: string, task_id: string) → {task_id, status}
- **FR-330**: System MUST expose delete_task MCP tool: delete_task(user_id: string, task_id: string) → {task_id, status}
- **FR-331**: System MUST expose update_task MCP tool: update_task(user_id: string, task_id: string, title?: string, description?: string) → {task_id, title, updated_at}

**MCP Tool Security & Validation**

- **FR-332**: Every MCP tool MUST verify user_id before any database operation
- **FR-333**: Every MCP tool MUST reject operations if user_id doesn't match task owner (403 Forbidden)
- **FR-334**: Every MCP tool MUST validate input parameters (title length, task_id format)
- **FR-335**: System MUST return 404 Not Found if task_id doesn't exist for user
- **FR-336**: System MUST handle task not found gracefully in agent response ("I couldn't find that task")
- **FR-337**: MCP tools MUST sanitize string inputs to prevent injection attacks
- **FR-338**: System MUST log all MCP tool invocations with user_id, tool_name, input, result, timestamp

**Tool Execution & Response Handling**

- **FR-339**: Agent MUST invoke minimal set of tools needed for current intent (no speculative calls)
- **FR-340**: Agent MUST handle tool errors gracefully and suggest next steps to user
- **FR-341**: Agent MUST retry transient errors (network timeouts) up to 2 times before escalating
- **FR-342**: Agent MUST include tool_calls array in response showing what was executed
- **FR-343**: Agent tool responses MUST include task IDs for user reference in future requests

**Conversation Management**

- **FR-344**: System MUST auto-generate conversation titles based on first message (optional override by user)
- **FR-345**: System MUST allow users to list all their conversations
- **FR-346**: System MUST allow users to retrieve conversation history (all messages in a conversation)
- **FR-347**: System MUST enforce user isolation: users only see their own conversations
- **FR-348**: Conversation records MUST include created_at and updated_at timestamps

**Input Validation & Sanitization**

- **FR-349**: System MUST validate task title: 1-200 characters, non-empty after trim
- **FR-350**: System MUST validate task description: 0-1000 characters (optional)
- **FR-351**: System MUST sanitize user message: remove leading/trailing whitespace, detect injection patterns
- **FR-352**: System MUST reject messages containing SQL injection patterns
- **FR-353**: System MUST reject messages containing JavaScript injection patterns

### Non-Functional Requirements

**Performance**

- **NFR-301**: Chat endpoint MUST respond in <5 seconds (P95) including agent execution
- **NFR-302**: MCP tool execution MUST complete in <2 seconds per tool
- **NFR-303**: Agent intent routing decision MUST occur in <1 second
- **NFR-304**: Database queries MUST complete in <100ms
- **NFR-305**: Conversation history retrieval MUST complete in <500ms even with 1000+ messages

**Scalability & Architecture**

- **NFR-306**: Chat endpoint MUST be stateless (no server-side session memory)
- **NFR-307**: Chat endpoint MUST support horizontal scaling (multiple instances)
- **NFR-308**: Agent MUST be instantiated fresh for each request (no persistent state)
- **NFR-309**: Database connection pooling MUST be enabled with min 10, max 20 connections
- **NFR-310**: System MUST handle 100 concurrent chat requests without degradation

**Data Persistence & Reliability**

- **NFR-311**: System MUST persist user messages before returning response (zero data loss)
- **NFR-312**: System MUST persist agent responses before returning to client
- **NFR-313**: Database transactions MUST be ACID compliant for message writes
- **NFR-314**: System MUST create database indexes on user_id and conversation_id for fast queries
- **NFR-315**: All database operations MUST use parameterized queries (no string concatenation)

**Audit & Observability**

- **NFR-316**: System MUST log all MCP tool invocations with timestamp, user_id, tool_name, input, output
- **NFR-317**: System MUST log all chat endpoint requests and responses (without exposing sensitive data)
- **NFR-318**: System MUST track performance metrics: response time, tool execution time, error rate
- **NFR-319**: System MUST maintain immutable conversation history (no deletion or modification of past messages)
- **NFR-320**: System MUST support audit trail queries (show all actions for a user_id)

**Security & Privacy**

- **NFR-321**: System MUST never expose user_id of other users in responses
- **NFR-322**: System MUST never expose task ownership details that reveal other users' existence
- **NFR-323**: System MUST enforce HTTPS for all chat endpoints in production
- **NFR-324**: System MUST validate all external inputs (user messages, HTTP headers)
- **NFR-325**: System MUST rate limit chat endpoint to 30 requests per minute per user

### Key Entities

- **Conversation**: Represents a chat thread for a user. Contains conversation_id, user_id, title (auto-generated or user-provided), created_at, updated_at. Groups related messages together.
- **Message**: Individual message in a conversation. Contains message_id, conversation_id, user_id, role (user/assistant), content, tool_calls (JSON array of executed tools), created_at. Immutable once created.
- **Task**: Existing entity from Phase II. Referenced by MCP tools. Contains task_id, user_id, title, description, completed (boolean), created_at, updated_at.
- **User**: Existing entity from Phase II (managed by Better Auth). Referenced in all conversations and tasks for isolation enforcement.

---

## Success Criteria

### Functional Success Criteria

- **SC-301**: User can add a task by typing "Add buy milk" and receive confirmation with task ID
- **SC-302**: User can list their pending tasks by typing "Show pending tasks" and receive formatted list
- **SC-303**: User can mark a task complete by typing "Mark task 1 done" and see status change reflected
- **SC-304**: User can update task title by typing "Change task 1 to 'buy milk and bread'" and see changes
- **SC-305**: User can delete a task by typing "Delete task 2", confirming, and seeing it removed
- **SC-306**: Agent correctly routes natural language variants ("add"/"create"/"remember") to add_task tool
- **SC-307**: Agent correctly routes natural language variants ("show"/"list"/"what's pending") to list_tasks tool
- **SC-308**: Agent asks for clarification when user intent is ambiguous (e.g., "Add milk and complete the list")
- **SC-309**: All tool invocations verify user_id and reject cross-user access attempts
- **SC-310**: Conversation history persists across requests and agent uses it for context

### Technical Success Criteria

- **SC-311**: Chat endpoint accepts POST requests to /api/{user_id}/chat with valid JWT
- **SC-312**: Chat endpoint rejects requests with invalid JWT (401) or mismatched user_id (403)
- **SC-313**: MCP tools all implement required signature with user_id parameter
- **SC-314**: Every MCP tool verifies user_id before DB access (user isolation verified in code review)
- **SC-315**: All MCP tool inputs validated: titles 1-200 chars, descriptions 0-1000 chars, IDs properly formatted
- **SC-316**: All responses include tool_calls array showing executed operations
- **SC-317**: Conversation records created and messages persisted on every successful chat request
- **SC-318**: Database queries use parameterized queries (no raw SQL or string concatenation)

### Performance Success Criteria

- **SC-319**: Chat endpoint P95 response time is <5 seconds across 100 concurrent requests
- **SC-320**: MCP tool execution completes in <2 seconds for add_task, list_tasks, complete_task, delete_task, update_task
- **SC-321**: Agent intent routing decision completes in <1 second
- **SC-322**: Database queries complete in <100ms, verified with database query logs
- **SC-323**: Conversation history retrieval completes in <500ms even with 1000+ messages in history
- **SC-324**: Chat endpoint maintains performance under sustained load (30 req/min/user for 1 hour)

### Security & Isolation Success Criteria

- **SC-325**: User cannot access another user's tasks through chat (tested by User A asking about User B's tasks)
- **SC-326**: User cannot access another user's conversation history (tested with conversation_id manipulation)
- **SC-327**: Tool invocations are logged with user_id, timestamp, tool_name for audit trail
- **SC-328**: Natural language inputs sanitized: SQL injection attempts rejected, XSS patterns sanitized
- **SC-329**: Responses never expose other users' data: no user IDs, no task ownership hints
- **SC-330**: Rate limiting prevents abuse: >30 requests/min/user are rejected with 429 Too Many Requests

### User Experience Success Criteria

- **SC-331**: Agent responses are natural and conversational (not robotic templates)
- **SC-332**: Agent confirms destructive actions (delete) before executing
- **SC-333**: Agent responses include what action was taken ("Task 1 'buy milk' created at 2026-01-12 10:30")
- **SC-334**: Error messages are user-friendly and suggest next steps ("Task not found. Would you like to see your pending tasks?")
- **SC-335**: Agent gracefully handles ambiguous input without failing ("I'm not sure if you want to create one task or two. Can you clarify?")
- **SC-336**: Multi-turn conversations maintain context (agent remembers previous messages in same conversation)
- **SC-337**: Users can start multiple independent conversations without confusion

### Integration Success Criteria

- **SC-338**: Chat endpoint integrates with Phase II Task CRUD endpoints (same tasks visible everywhere)
- **SC-339**: Chat endpoint uses Phase II JWT authentication (same BETTER_AUTH_SECRET)
- **SC-340**: Chat endpoint enforces Phase II user isolation patterns (same user_id validation)
- **SC-341**: MCP tools follow Phase II Pydantic validation patterns
- **SC-342**: Conversation/Message tables follow Phase II SQLModel schema patterns

---

## Database Models (New for Phase III)

### Conversation Table

```typescript
interface Conversation {
  id: string;              // UUID primary key
  user_id: string;         // Foreign key to users.id
  title: string;           // Auto-generated or user-provided (max 500 chars)
  created_at: string;      // ISO timestamp, auto-generated
  updated_at: string;      // ISO timestamp, auto-updated
}

// Constraints:
// - PRIMARY KEY (id)
// - FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
// - INDEX ON (user_id, updated_at) for fast retrieval of user's conversations
// - NOT NULL: id, user_id, created_at
```

### Message Table

```typescript
interface Message {
  id: string;              // UUID primary key
  conversation_id: string; // Foreign key to conversations.id
  user_id: string;         // Foreign key to users.id (denormalized for fast filtering)
  role: string;            // "user" or "assistant"
  content: string;         // Message text (max 10000 chars)
  tool_calls: string;      // JSON array of tool executions (nullable)
  created_at: string;      // ISO timestamp, auto-generated (immutable)
}

// Constraints:
// - PRIMARY KEY (id)
// - FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
// - FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
// - INDEX ON (conversation_id, created_at) for fast message retrieval
// - INDEX ON (user_id) for audit trail queries
// - NOT NULL: id, conversation_id, user_id, role, content, created_at
// - CHECK (role IN ('user', 'assistant'))
```

### Tool Calls JSON Schema

```typescript
interface ToolCall {
  tool_name: string;       // "add_task", "list_tasks", etc.
  input: object;           // Tool input parameters
  result: object;          // Tool output/result
  executed_at: string;     // ISO timestamp when tool was executed
  error?: string;          // Optional error message if tool failed
}
```

---

## Chat API Contract

### Chat Request Endpoint

```
POST /api/{user_id}/chat
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "conversation_id": "optional-uuid",  // If continuing existing conversation
  "message": "Add buy milk"
}
```

### Chat Response - Success (200 OK)

```json
{
  "id": "msg-uuid-123",
  "conversation_id": "conv-uuid-456",
  "user_id": "user-uuid-789",
  "content": "Great! I've added 'buy milk' to your tasks. It's now task #5.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "input": {
        "user_id": "user-uuid-789",
        "title": "buy milk"
      },
      "result": {
        "task_id": 5,
        "title": "buy milk",
        "created_at": "2026-01-12T10:30:00Z"
      },
      "executed_at": "2026-01-12T10:30:00.123Z"
    }
  ],
  "created_at": "2026-01-12T10:30:00Z"
}
```

### Chat Response - Clarification Request (200 OK)

```json
{
  "id": "msg-uuid-234",
  "conversation_id": "conv-uuid-456",
  "user_id": "user-uuid-789",
  "content": "I'm not sure what you're asking. Do you want to: (1) Add a single task called 'milk and bread', or (2) Add two separate tasks 'milk' and 'bread'?",
  "tool_calls": [],
  "created_at": "2026-01-12T10:31:00Z"
}
```

### Error Response - Invalid JWT (401 Unauthorized)

```json
{
  "detail": "Invalid or missing authorization token"
}
```

### Error Response - User Mismatch (403 Forbidden)

```json
{
  "detail": "User ID in token does not match request path"
}
```

### Error Response - Missing Message (400 Bad Request)

```json
{
  "detail": "Message field is required and cannot be empty"
}
```

### Error Response - Invalid Conversation (404 Not Found)

```json
{
  "detail": "Conversation not found for this user"
}
```

### Error Response - Agent Error (500 Internal Server Error)

```json
{
  "detail": "Sorry, I encountered an error processing your request. Please try again."
}
```

---

## MCP Tools Specification

### Tool 1: add_task

**Purpose**: Create a new task for the user

**Input Schema**:
```typescript
{
  user_id: string;        // Required: UUID of authenticated user
  title: string;          // Required: 1-200 characters, non-empty after trim
  description?: string;   // Optional: 0-1000 characters
}
```

**Output Schema**:
```typescript
{
  task_id: number;        // Auto-incremented task ID
  user_id: string;        // User who owns this task
  title: string;          // Task title as created
  description?: string;   // Task description if provided
  completed: boolean;     // Always false for new tasks
  created_at: string;     // ISO timestamp
}
```

**Validation**:
- Verify user_id matches authenticated user (403 if mismatch)
- Verify title length: 1-200 characters, trim whitespace
- Verify description length if provided: 0-1000 characters
- Sanitize inputs for injection attacks

**Database Operation**: INSERT into tasks table

**Error Handling**:
- Return 400 if title empty or >200 chars
- Return 400 if description >1000 chars
- Return 500 if database insert fails (log error, don't expose)

---

### Tool 2: list_tasks

**Purpose**: Retrieve user's tasks, optionally filtered by completion status

**Input Schema**:
```typescript
{
  user_id: string;        // Required: UUID of authenticated user
  filter?: string;        // Optional: "pending" (incomplete) or "completed" or "all" (default: "pending")
}
```

**Output Schema**:
```typescript
[
  {
    id: number;
    user_id: string;
    title: string;
    description?: string;
    completed: boolean;
    created_at: string;
    updated_at: string;
  }
]
```

**Validation**:
- Verify user_id matches authenticated user (403 if mismatch)
- Validate filter parameter: only "pending", "completed", "all" accepted
- Default to "pending" if filter not provided

**Database Operation**: SELECT from tasks WHERE user_id=? AND (completed=? OR filter="all")

**Error Handling**:
- Return 400 if filter invalid
- Return empty array [] if no tasks match filter (not an error)
- Return 500 if query fails

---

### Tool 3: complete_task

**Purpose**: Mark a task as complete

**Input Schema**:
```typescript
{
  user_id: string;        // Required: UUID of authenticated user
  task_id: number;        // Required: ID of task to complete
}
```

**Output Schema**:
```typescript
{
  task_id: number;
  user_id: string;
  title: string;
  completed: boolean;     // Should be true after completion
  updated_at: string;     // ISO timestamp of update
}
```

**Validation**:
- Verify user_id matches authenticated user (403 if mismatch)
- Verify task_id exists and belongs to user (404 if not found or user mismatch)
- Prevent idempotent errors: if task already completed, return success (not error)

**Database Operation**: UPDATE tasks SET completed=true WHERE id=? AND user_id=?

**Error Handling**:
- Return 404 if task_id doesn't exist
- Return 403 if task belongs to different user
- Return 500 if update fails

---

### Tool 4: update_task

**Purpose**: Modify task title and/or description

**Input Schema**:
```typescript
{
  user_id: string;        // Required: UUID of authenticated user
  task_id: number;        // Required: ID of task to update
  title?: string;         // Optional: new title (1-200 chars if provided)
  description?: string;   // Optional: new description (0-1000 chars if provided)
}
```

**Output Schema**:
```typescript
{
  task_id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  updated_at: string;     // ISO timestamp of update
}
```

**Validation**:
- Verify user_id matches authenticated user (403 if mismatch)
- Verify task_id exists and belongs to user (404 if not found)
- If title provided: validate 1-200 characters
- If description provided: validate 0-1000 characters
- Require at least one of title or description to be provided (400 if both missing)

**Database Operation**: UPDATE tasks SET title=?, description=?, updated_at=NOW() WHERE id=? AND user_id=?

**Error Handling**:
- Return 404 if task_id doesn't exist
- Return 403 if task belongs to different user
- Return 400 if title/description invalid length
- Return 400 if neither title nor description provided
- Return 500 if update fails

---

### Tool 5: delete_task

**Purpose**: Permanently remove a task

**Input Schema**:
```typescript
{
  user_id: string;        // Required: UUID of authenticated user
  task_id: number;        // Required: ID of task to delete
}
```

**Output Schema**:
```typescript
{
  task_id: number;
  status: "deleted";
  message: string;        // e.g., "Task 1 'buy milk' has been deleted"
}
```

**Validation**:
- Verify user_id matches authenticated user (403 if mismatch)
- Verify task_id exists and belongs to user (404 if not found)

**Database Operation**: DELETE FROM tasks WHERE id=? AND user_id=?

**Error Handling**:
- Return 404 if task_id doesn't exist
- Return 403 if task belongs to different user
- Return 500 if delete fails

---

## Agent Behavior Specification

### Intent Recognition Patterns

The agent MUST map natural language to one of six intents:

| User Input Pattern | Intent | MCP Tool(s) | Example |
|-------------------|--------|-------------|---------|
| "Add/Create/Remember/Put/Don't forget [task]" | CREATE | add_task | "Add buy milk" |
| "Show/List/What's/Tell me/Display [tasks]" | LIST | list_tasks | "Show pending tasks" |
| "Done/Finished/Complete/Mark [task] complete" | COMPLETE | complete_task | "Mark task 1 done" |
| "Change/Update/Rename/Modify [task] to [new]" | UPDATE | update_task | "Change task 1 to 'buy milk and bread'" |
| "Delete/Remove/Get rid of/Drop [task]" | DELETE | delete_task | "Delete task 2" |
| "Ambiguous/unclear input" | CLARIFY | none | "Do this and that" |

### Intent Routing Logic

1. **Pattern Matching**: Agent analyzes user message for intent keywords
2. **Context Consideration**: Uses conversation history to resolve ambiguities
3. **Confidence Check**: If confidence <70%, escalate to CLARIFY intent
4. **Tool Selection**: Invoke minimal set of tools for the detected intent
5. **Response Generation**: Provide natural, conversational confirmation

### Handling Ambiguous Intent

When user message could map to multiple intents:
- Ask clarifying question with numbered options
- Wait for user to select/clarify
- Don't proceed with wrong action
- Example: User says "Add milk and complete the list" → Agent asks "Do you mean (1) create a task, or (2) create and mark another task complete?"

### Natural Language Variations

Agent MUST recognize these variations:

**CREATE variations**: "add", "create", "remember", "put", "don't forget", "I need to", "remind me to"

**LIST variations**: "show", "list", "what's", "what do I", "tell me", "display", "view", "pending", "coming up"

**COMPLETE variations**: "done", "finished", "complete", "mark", "check off", "got it", "take care of"

**UPDATE variations**: "change", "update", "rename", "modify", "fix", "correct", "edit"

**DELETE variations**: "delete", "remove", "get rid of", "drop", "trash", "erase", "forget about"

### Tool Invocation Order

When agent routes to tools, execution order:
1. **Validation tools** execute first (validate inputs, check permissions)
2. **Read tools** execute before write tools when both needed
3. **Critical tools** (delete) execute last after confirmation
4. Multiple tools in same category execute in parallel if independent

### Error Recovery Strategy

| Error | Agent Response | Next Action |
|-------|----------------|-------------|
| Tool returns 404 (task not found) | "I couldn't find that task. Would you like to see your task list?" | Offer list_tasks |
| Tool returns 400 (invalid input) | "I need more details. [specific request]" | Ask for clarification |
| Tool returns 403 (permission denied) | "You don't have permission to access that task" | Stop, no retry |
| Tool returns 500 (server error) | "Sorry, I'm having trouble. Please try again in a moment" | Don't retry automatically |
| Tool timeout (>2s) | "That took too long. Let me try again" | Retry once, then fail gracefully |

### Response Format Requirements

All agent responses MUST:
1. **Natural**: Use conversational language, not robotic templates
2. **Confirmatory**: State what action was taken (e.g., "I've added 'buy milk' to your tasks")
3. **Informative**: Include task ID/name for reference in future requests
4. **Tool-Transparent**: Include tool_calls array showing executed operations
5. **Actionable**: Suggest next steps if applicable ("Would you like to see your full task list?")

---

## Assumptions

- Users prefer conversational interaction over form-based interfaces for quick task entry
- Users are willing to provide additional clarification when agent request
- Conversation history provides sufficient context for multi-turn interactions (no long-term memory needed beyond session)
- Chat endpoint will be accessed from authenticated frontend (not public API)
- Performance targets (5s response, <2s tool execution) are achievable with proper indexing
- Users trust that tasks created via chat will persist in task list (checked regularly)
- Agent will be powered by OpenAI API (gpt-4o or latest reasoning model)
- MCP SDK provides reliable tool execution framework with proper error handling

