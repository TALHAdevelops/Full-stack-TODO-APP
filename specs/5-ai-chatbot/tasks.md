# TaskFlow Phase III - AI Chatbot Task Breakdown

**Feature Branch**: `5-ai-chatbot`
**Created**: 2026-01-13
**Total Tasks**: 37
**Task Range**: T-301 to T-337

---

## Status Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 37 |
| **Completed** | 33 |
| **In Progress** | 0 |
| **Remaining** | 4 |

---

## Phase Overview

| Phase | ID Range | Title | Tasks | Dependencies |
|-------|----------|-------|-------|--------------|
| **A** | T-301 to T-305 | Database & Models | 5 | None |
| **B** | T-306 to T-320 | MCP Server & Tools | 15 | Phase A |
| **C** | T-321 to T-327 | Agent & Chat Endpoint | 7 | Phase B |
| **D** | T-328 to T-333 | Frontend ChatKit | 6 | Phase C |
| **E** | T-334 to T-337 | Testing & Deployment | 4 | Phase D |

---

## Phase A: Database & Models (T-301 to T-305)

**Goal**: Create database schema and SQLModel classes for conversations and messages

| Task ID | Title | Status | Dependency |
|---------|-------|--------|------------|
| T-301 | Create Conversation SQLModel | [x] | None |
| T-302 | Create Message SQLModel | [x] | T-301 |
| T-303 | Add database migration for conversations table | [x] | T-301 |
| T-304 | Add database migration for messages table | [x] | T-302 |
| T-305 | Create database indexes and constraints | [x] | T-304 |

### Detailed Task Definitions

**T-301: Create Conversation SQLModel**

- **Description**: Add Conversation SQLModel class to `backend/models.py`
- **Acceptance Criteria**:
  - Conversation class with fields: `id` (UUID, PK), `user_id` (FK to users.id), `title` (string, nullable), `created_at` (timestamp), `updated_at` (timestamp)
  - Foreign key constraint on `user_id` references `users.id`
  - All timestamp fields default to `datetime.utcnow()`
  - Table name is `conversations` (lowercase, plural)
  - Class inherits from `SQLModel` with `table=True`
- **Files**: `backend/models.py`
- **References**: [spec.md: Data Requirements], [plan.md: Database Schema]

---

**T-302: Create Message SQLModel**

- **Description**: Add Message SQLModel class to `backend/models.py`
- **Acceptance Criteria**:
  - Message class with fields: `id` (UUID, PK), `conversation_id` (FK), `user_id` (FK), `role` (Literal["user", "assistant"]), `content` (string), `tool_calls` (JSON, nullable), `created_at` (timestamp)
  - Foreign key constraints: `conversation_id` → `conversations.id`, `user_id` → `users.id`
  - `role` field restricted to "user" or "assistant"
  - Table name is `messages` (lowercase, plural)
  - All timestamps default to `datetime.utcnow()`
  - `tool_calls` stores JSON array of tool execution records (optional)
- **Files**: `backend/models.py`
- **References**: [spec.md: Message Structure], [plan.md: Message Table]

---

**T-303: Add database migration for conversations table**

- **Description**: Create and run Alembic migration to create `conversations` table in Neon PostgreSQL
- **Acceptance Criteria**:
  - Migration file generated in `backend/alembic/versions/`
  - Migration creates `conversations` table with UUID primary key
  - Foreign key constraint on `user_id` with CASCADE delete
  - Indexes created on `user_id` for quick lookups
  - Migration is reversible (includes downgrade)
  - Migration runs without errors: `alembic upgrade head`
  - Table is queryable in database
- **Files**: `backend/alembic/versions/*.py`, `backend/alembic/env.py`
- **References**: [plan.md: Database Schema]

---

**T-304: Add database migration for messages table**

- **Description**: Create and run Alembic migration to create `messages` table in Neon PostgreSQL
- **Acceptance Criteria**:
  - Migration file generated in `backend/alembic/versions/`
  - Migration creates `messages` table with UUID primary key
  - Foreign key constraints: `conversation_id` → CASCADE, `user_id` → CASCADE
  - `role` column uses CHECK constraint or ENUM type (PostgreSQL)
  - `tool_calls` column is JSON type (jsonb in PostgreSQL)
  - Indexes created on `conversation_id` and `user_id`
  - Migration runs without errors: `alembic upgrade head`
  - Table is queryable in database
- **Files**: `backend/alembic/versions/*.py`
- **References**: [plan.md: Database Schema]

---

**T-305: Create database indexes and constraints**

- **Description**: Add performance indexes and enforce data integrity constraints
- **Acceptance Criteria**:
  - Index on `conversations(user_id)` for fast user lookup
  - Index on `messages(conversation_id)` for fast conversation history retrieval
  - Index on `messages(user_id, created_at DESC)` for recent user messages
  - Unique constraint on conversation title per user (optional: `conversations(user_id, title)`)
  - Check constraint: `messages.role IN ('user', 'assistant')`
  - All indexes are created via Alembic migration
  - Query plans show index usage (verified with EXPLAIN)
  - No N+1 query issues when loading conversation history
- **Files**: `backend/alembic/versions/*.py`
- **References**: [plan.md: Database Optimization]

---

## Phase B: MCP Server & Tools (T-306 to T-320)

**Goal**: Implement MCP server with 5 task management tools (add, list, complete, update, delete)

| Task ID | Title | Status | Dependency |
|---------|-------|--------|------------|
| T-306 | Create MCP server scaffolding | [x] | T-305 |
| T-307 | Implement add_task MCP tool | [x] | T-306 |
| T-308 | Implement list_tasks MCP tool | [x] | T-306 |
| T-309 | Implement complete_task MCP tool | [x] | T-306 |
| T-310 | Implement update_task MCP tool | [x] | T-306 |
| T-311 | Implement delete_task MCP tool | [x] | T-306 |
| T-312 | Add input validation for all tools | [x] | T-307 to T-311 |
| T-313 | Add user isolation verification | [x] | T-312 |
| T-314 | Add error handling and logging | [x] | T-313 |
| T-315 | Create tool response schemas | [x] | T-314 |
| T-316 | Create MCP tool documentation | [x] | T-315 |
| T-317 | Test add_task tool with manual API calls | [x] | T-316 |
| T-318 | Test list_tasks tool with multiple filters | [x] | T-316 |
| T-319 | Test complete_task and update_task tools | [x] | T-316 |
| T-320 | Test delete_task tool with error cases | [x] | T-316 |

### Detailed Task Definitions

**T-306: Create MCP server scaffolding**

- **Description**: Set up MCP server infrastructure in `backend/mcp_server.py`
- **Acceptance Criteria**:
  - File `backend/mcp_server.py` created with MCP SDK import and initialization
  - MCP server class created with method stubs for 5 tools
  - Server implements Model Context Protocol spec
  - Each tool returns structured response with `{status, data, error?}` format
  - MCP server can be started as subprocess: `python -m backend.mcp_server`
  - Logs initialization message: "MCP Server started, listening for tool calls"
  - No runtime errors on startup
- **Files**: `backend/mcp_server.py`
- **References**: [plan.md: MCP Server Architecture], [spec.md: MCP Tools]

---

**T-307: Implement add_task MCP tool**

- **Description**: Build add_task tool that creates new tasks from agent requests
- **Acceptance Criteria**:
  - Function signature: `add_task(user_id: str, title: str, description: Optional[str] = None) → dict`
  - Accepts parameters: `user_id`, `title` (1-200 chars), `description` (0-1000 chars, optional)
  - Validates user_id format (non-empty, valid UUID)
  - Validates title: not empty, trim whitespace, max 200 chars
  - Validates description: max 1000 chars if provided
  - Creates Task record with `completed=False`, `created_at=now()`
  - Returns: `{task_id, user_id, title, description, created_at}`
  - Raises ValueError with clear message for invalid inputs
  - Raises DatabaseError with generic message on DB failure
- **Files**: `backend/mcp_server.py`
- **References**: [spec.md: FR-327], [plan.md: MCP Tools]

---

**T-308: Implement list_tasks MCP tool**

- **Description**: Build list_tasks tool that retrieves user's tasks with optional filtering
- **Acceptance Criteria**:
  - Function signature: `list_tasks(user_id: str, filter: Optional[str] = None) → list[dict]`
  - Supports filters: "pending" (completed=false), "completed" (completed=true), None (all)
  - Query: `SELECT id, title, description, completed, created_at FROM tasks WHERE user_id=? AND (filter applied)`
  - Returns sorted by `created_at DESC` (newest first)
  - Returns empty list if user has no tasks (not error)
  - Each task includes: `{id, title, description, completed, created_at}`
  - Verifies user_id ownership before returning (no cross-user leakage)
  - Handles missing user_id gracefully
- **Files**: `backend/mcp_server.py`
- **References**: [spec.md: FR-328], [plan.md: MCP Tools]

---

**T-309: Implement complete_task MCP tool**

- **Description**: Build complete_task tool that marks tasks as done
- **Acceptance Criteria**:
  - Function signature: `complete_task(user_id: str, task_id: str) → dict`
  - Validates task_id ownership: query `SELECT * FROM tasks WHERE id=? AND user_id=?`
  - If task not found: raise ValueError("Task not found")
  - If task already completed: raise ValueError("Task already completed")
  - Updates: `UPDATE tasks SET completed=true, updated_at=now() WHERE id=?`
  - Returns: `{task_id, status: "completed", completed_at: timestamp}`
  - Does not allow completing tasks owned by other users (403)
  - Logs action with user_id and task_id
- **Files**: `backend/mcp_server.py`
- **References**: [spec.md: FR-329], [plan.md: MCP Tools]

---

**T-310: Implement update_task MCP tool**

- **Description**: Build update_task tool that modifies task title or description
- **Acceptance Criteria**:
  - Function signature: `update_task(user_id: str, task_id: str, title: Optional[str] = None, description: Optional[str] = None) → dict`
  - Validates task_id ownership before update
  - If task not found: raise ValueError("Task not found")
  - At least one of title or description must be provided, else raise ValueError
  - Validates new title: 1-200 chars if provided
  - Validates new description: 0-1000 chars if provided
  - Updates only non-null fields: `UPDATE tasks SET title=?, description=?, updated_at=now() WHERE id=?`
  - Returns: `{task_id, title, description, updated_at}`
  - Preserves original fields if not updated
- **Files**: `backend/mcp_server.py`
- **References**: [spec.md: FR-331], [plan.md: MCP Tools]

---

**T-311: Implement delete_task MCP tool**

- **Description**: Build delete_task tool that removes tasks permanently
- **Acceptance Criteria**:
  - Function signature: `delete_task(user_id: str, task_id: str) → dict`
  - Validates task_id ownership before deletion
  - If task not found: raise ValueError("Task not found")
  - Executes: `DELETE FROM tasks WHERE id=? AND user_id=?`
  - Returns: `{task_id, status: "deleted", deleted_at: timestamp}`
  - Does not allow deleting tasks owned by other users (403)
  - Logs deletion with user_id, task_id, timestamp
  - After deletion, subsequent queries for task return 404
- **Files**: `backend/mcp_server.py`
- **References**: [spec.md: FR-330], [plan.md: MCP Tools]

---

**T-312: Add input validation for all tools**

- **Description**: Enforce consistent validation across all 5 MCP tools
- **Acceptance Criteria**:
  - User_id validation: non-empty, valid UUID format (or alphanumeric string)
  - Task_id validation: non-empty, valid UUID or integer format
  - Title validation: non-empty after trim, max 200 chars, no injection attempts
  - Description validation: max 1000 chars, sanitized input
  - All string inputs sanitized for SQL injection (via SQLModel parameterization)
  - Filter parameter restricted to: "pending", "completed", None
  - Invalid inputs raise ValueError with specific error message
  - Error messages do not expose database structure or internals
- **Files**: `backend/mcp_server.py`, create `backend/validators.py` if needed
- **References**: [spec.md: FR-334, FR-337], [plan.md: Security]

---

**T-313: Add user isolation verification**

- **Description**: Enforce that tools cannot access or modify tasks from other users
- **Acceptance Criteria**:
  - Every tool includes user_id parameter
  - Every database query includes `AND user_id=?` condition
  - Every update/delete includes `AND user_id=?` in WHERE clause
  - Tool response never leaks user_id or other users' data
  - Attempted cross-user access returns ValueError("Unauthorized")
  - Logs security violation with attacker user_id
  - No information leakage on ownership mismatch (doesn't say "user X owns this")
- **Files**: `backend/mcp_server.py`
- **References**: [spec.md: FR-332, FR-333], [plan.md: Security]

---

**T-314: Add error handling and logging**

- **Description**: Implement robust error handling and audit logging for all tools
- **Acceptance Criteria**:
  - All tool calls wrapped in try-except
  - Database errors caught and return generic error: "Database operation failed"
  - Network timeouts handled with retry logic (1 retry)
  - Invalid inputs raise ValueError with descriptive message
  - All tool invocations logged: user_id, tool_name, input params, result/error, timestamp
  - Logs written to `backend/logs/mcp_tools.log`
  - No sensitive data in logs (no passwords, no full task content, no full user data)
  - Error responses include `{status: "error", message: "...", code: "..."}`
- **Files**: `backend/mcp_server.py`, `backend/logger.py`
- **References**: [spec.md: FR-341], [plan.md: Error Handling]

---

**T-315: Create tool response schemas**

- **Description**: Define Pydantic response models for all tool outputs
- **Acceptance Criteria**:
  - Create `backend/schemas/mcp_responses.py`
  - Define response schemas:
    - `AddTaskResponse: {task_id, user_id, title, created_at}`
    - `ListTasksResponse: list[{id, title, completed, created_at}]`
    - `CompleteTaskResponse: {task_id, status, completed_at}`
    - `UpdateTaskResponse: {task_id, title, updated_at}`
    - `DeleteTaskResponse: {task_id, status, deleted_at}`
    - `ErrorResponse: {status, message, code}`
  - All schemas use proper types (UUID, datetime, bool, str)
  - Schemas enforce required vs. optional fields
  - Tool implementations return instances of these schemas
- **Files**: `backend/schemas/mcp_responses.py`
- **References**: [plan.md: Response Contracts]

---

**T-316: Create MCP tool documentation**

- **Description**: Write OpenAPI/docstring documentation for all tools
- **Acceptance Criteria**:
  - Each tool function has docstring with: description, parameters, returns, raises
  - Example docstring:
    ```python
    def add_task(user_id: str, title: str, description: Optional[str] = None) -> dict:
        """
        Create a new task for a user.

        Args:
            user_id: UUID of the user creating the task
            title: Task title (1-200 characters)
            description: Optional task description (0-1000 characters)

        Returns:
            {task_id, user_id, title, created_at}

        Raises:
            ValueError: If inputs invalid or user not found
        """
    ```
  - Document supported tool inputs in `backend/MCP_TOOLS.md`
  - Include usage examples for each tool
  - Document error codes and responses
- **Files**: `backend/mcp_server.py`, `backend/MCP_TOOLS.md`
- **References**: [plan.md: MCP Documentation]

---

**T-317: Test add_task tool with manual API calls**

- **Description**: Manually test add_task tool functionality
- **Acceptance Criteria**:
  - Start MCP server: `python -m backend.mcp_server`
  - Call add_task with valid inputs: title="Buy milk" → task_id returned
  - Call add_task with empty title → ValueError raised
  - Call add_task with title > 200 chars → ValueError raised
  - Call add_task with invalid user_id → ValueError raised
  - Call add_task with description > 1000 chars → ValueError raised
  - Task persists in database after call
  - Multiple tasks for same user have different task_ids
  - Test script: `backend/tests/test_add_task.py`
- **Files**: `backend/tests/test_add_task.py`
- **References**: [spec.md: FR-327], [plan.md: Testing]

---

**T-318: Test list_tasks tool with multiple filters**

- **Description**: Test list_tasks tool with various filter combinations
- **Acceptance Criteria**:
  - Create 3 test tasks (2 pending, 1 completed)
  - Call list_tasks(user_id, filter=None) → returns all 3
  - Call list_tasks(user_id, filter="pending") → returns 2 pending
  - Call list_tasks(user_id, filter="completed") → returns 1 completed
  - Call list_tasks with no tasks → returns empty list (not error)
  - Call list_tasks with another user_id → returns only that user's tasks
  - Tasks sorted by created_at DESC (newest first)
  - Each task includes: id, title, completed, created_at
  - Test script: `backend/tests/test_list_tasks.py`
- **Files**: `backend/tests/test_list_tasks.py`
- **References**: [spec.md: FR-328], [plan.md: Testing]

---

**T-319: Test complete_task and update_task tools**

- **Description**: Test state mutation tools (complete and update)
- **Acceptance Criteria**:
  - Create test task: title="Buy milk"
  - Call complete_task(user_id, task_id) → task marked completed
  - Query database: task.completed == True, updated_at set
  - Call complete_task again → ValueError("Task already completed")
  - Call update_task(task_id, title="Buy milk and bread") → title updated
  - Query database: task.title == "Buy milk and bread"
  - Call update_task with invalid task_id → ValueError("Task not found")
  - Call update_task(task_id, description="High priority") → description updated
  - Test script: `backend/tests/test_mutations.py`
- **Files**: `backend/tests/test_mutations.py`
- **References**: [spec.md: FR-329, FR-331], [plan.md: Testing]

---

**T-320: Test delete_task tool with error cases**

- **Description**: Test delete_task with various error scenarios
- **Acceptance Criteria**:
  - Create test task
  - Call delete_task(user_id, task_id) → task deleted
  - Query database: task not found
  - Call delete_task(user_id, task_id) again → ValueError("Task not found")
  - Create task as user A, attempt delete as user B → ValueError("Unauthorized")
  - Test with invalid task_id → ValueError("Task not found")
  - Test with invalid user_id → ValueError raised
  - Logs show all deletion attempts (including failed)
  - Test script: `backend/tests/test_delete_task.py`
- **Files**: `backend/tests/test_delete_task.py`
- **References**: [spec.md: FR-330], [plan.md: Testing]

---

## Phase C: Agent & Chat Endpoint (T-321 to T-327)

**Goal**: Implement OpenAI Agent SDK wrapper and chat HTTP endpoint

| Task ID | Title | Status | Dependency |
|---------|-------|--------|------------|
| T-321 | Create agent wrapper with system prompt | [x] | T-320 |
| T-322 | Implement intent routing and tool selection | [x] | T-321 |
| T-323 | Create chat endpoint route handler | [x] | T-321 |
| T-324 | Implement JWT validation and user extraction | [x] | T-323 |
| T-325 | Implement conversation history persistence | [x] | T-324 |
| T-326 | Add error handling and graceful failures | [x] | T-325 |
| T-327 | Manual test of full chat flow | [ ] | T-326 |

### Detailed Task Definitions

**T-321: Create agent wrapper with system prompt**

- **Description**: Build OpenAI Agent SDK wrapper in `backend/agents.py`
- **Acceptance Criteria**:
  - File `backend/agents.py` created
  - Function `create_agent(tools: list, model: str = "gpt-4o") → Agent`
  - System prompt includes task management instructions and tool descriptions
  - System prompt explains natural language variations (add/create/remember, etc.)
  - System prompt includes: "Ask for clarification if request is ambiguous"
  - System prompt instructs agent to include tool_calls in response
  - Agent initialized with all 5 MCP tools (add_task, list_tasks, complete_task, update_task, delete_task)
  - Agent runs on message + conversation history context
  - Agent uses gpt-4o model by default
  - No runtime errors on agent initialization
- **Files**: `backend/agents.py`
- **References**: [plan.md: Agent Architecture], [spec.md: Agent Behavior]

---

**T-322: Implement intent routing and tool selection**

- **Description**: Add intelligent tool selection based on user message intent
- **Acceptance Criteria**:
  - Function `parse_intent(message: str) → str` returns one of: CREATE, LIST, COMPLETE, UPDATE, DELETE, CLARIFY
  - Intent parsing recognizes variations:
    - CREATE: "add", "create", "remember", "make", "new task"
    - LIST: "show", "list", "pending", "what", "view"
    - COMPLETE: "done", "complete", "finished", "mark"
    - UPDATE: "change", "update", "rename", "modify"
    - DELETE: "delete", "remove", "get rid"
    - CLARIFY: ambiguous or multiple intents detected
  - Function `select_tools(intent: str) → list[str]` returns minimal set of tools needed
  - Agent invokes only necessary tools (no speculative calls)
  - Conversation history considered for context (reference to previous task)
  - Unclear messages routed to CLARIFY intent (agent asks questions)
- **Files**: `backend/agents.py`
- **References**: [plan.md: Intent Routing], [spec.md: FR-318-FR-326]

---

**T-323: Create chat endpoint route handler**

- **Description**: Build POST `/api/{user_id}/chat` endpoint in `backend/routes/chat.py`
- **Acceptance Criteria**:
  - Route file `backend/routes/chat.py` created
  - Endpoint: `POST /api/{user_id}/chat`
  - Request body: `{conversation_id?: string, message: string}`
  - Response body: `{id: string, conversation_id: string, user_id: string, content: string, tool_calls: array, created_at: string}`
  - Validates message is not empty (400 Bad Request if empty)
  - Validates message length ≤ 5000 chars (400 Bad Request if longer)
  - Creates new conversation if `conversation_id` not provided
  - Fetches existing conversation by `conversation_id` (404 if not found or wrong user)
  - Calls agent with conversation history
  - Stores both user and assistant messages in database
  - Returns structured response with tool_calls array
  - Proper HTTP status codes: 200, 400, 401, 403, 404, 500
- **Files**: `backend/routes/chat.py`
- **References**: [spec.md: FR-301, FR-306-FR-310], [plan.md: Chat Endpoint]

---

**T-324: Implement JWT validation and user extraction**

- **Description**: Add JWT token validation and user_id extraction to chat endpoint
- **Acceptance Criteria**:
  - Validates Authorization header format: "Bearer <token>"
  - Returns 401 Unauthorized if header missing or malformed
  - Decodes JWT using BETTER_AUTH_SECRET (shared secret)
  - Extracts user_id from JWT payload
  - Returns 401 Unauthorized if token invalid or expired
  - Verifies JWT user_id matches URL path parameter user_id
  - Returns 403 Forbidden if mismatch
  - Middleware or endpoint decorator handles validation
  - No unhandled JWT errors (all caught and return proper HTTP status)
  - Works with same JWT generation as Phase II (Better Auth compatible)
- **Files**: `backend/routes/chat.py`, `backend/middleware/auth.py`
- **References**: [spec.md: FR-302-FR-305], [plan.md: Security]

---

**T-325: Implement conversation history persistence**

- **Description**: Fetch, store, and manage conversation history in database
- **Acceptance Criteria**:
  - Function `fetch_conversation_history(conversation_id, user_id, limit=20) → list[Message]`
  - Retrieves up to 20 most recent messages from database
  - Filters: only messages from conversation_id and user_id (user isolation)
  - Orders by created_at ASC (oldest first for context)
  - Returns empty list if conversation not found
  - Function `store_message(conversation_id, user_id, role, content, tool_calls)` inserts message
  - Stores both user messages (role="user") and assistant messages (role="assistant")
  - Automatically sets created_at timestamp
  - Returns stored message with id
  - Conversation metadata (title, updated_at) updated when new message added
  - No N+1 queries when loading history
- **Files**: `backend/routes/chat.py`, `backend/services/conversation_service.py`
- **References**: [spec.md: FR-312-FR-317], [plan.md: Persistence]

---

**T-326: Add error handling and graceful failures**

- **Description**: Implement comprehensive error handling for chat endpoint
- **Acceptance Criteria**:
  - All tool invocation errors caught and logged
  - Agent errors return generic message: "Sorry, I couldn't complete that action. Please try again"
  - Database errors return: "Database operation failed. Please try again"
  - Network timeouts trigger 1 retry, then: "Service temporarily unavailable"
  - Invalid user_id: proper error message without exposing internals
  - Conversation not found: 404 with message
  - User account deleted: "Your account has been deleted"
  - All errors logged with user_id, timestamp, full error details
  - No stack traces returned to client
  - Response always returns valid JSON even on error
  - Error response format: `{error: string, code: string, timestamp: string}`
- **Files**: `backend/routes/chat.py`, `backend/utils/error_handler.py`
- **References**: [spec.md: Edge Cases], [plan.md: Error Handling]

---

**T-327: Manual test of full chat flow**

- **Description**: End-to-end test of complete chat workflow
- **Acceptance Criteria**:
  - Start backend: `uvicorn backend.main:app --reload`
  - Create test user with valid JWT token
  - POST `/api/{user_id}/chat` with message "Add buy milk"
  - Response includes: conversation_id, message_id, tool_calls array showing add_task invoked
  - POST same endpoint with new message "Show pending tasks" in same conversation
  - Response shows list_tasks tool invoked, returns tasks created
  - Task appears in response list with correct title
  - Continue conversation: "Mark task 1 complete"
  - Response shows complete_task tool invoked, task marked complete
  - Query database: messages and conversations persisted correctly
  - Test script: `backend/tests/test_full_chat_flow.py`
- **Files**: `backend/tests/test_full_chat_flow.py`
- **References**: [spec.md: All User Stories], [plan.md: System Architecture]

---

## Phase D: Frontend ChatKit (T-328 to T-333)

**Goal**: Build React chat interface with real-time message display and input

| Task ID | Title | Status | Dependency |
|---------|-------|--------|------------|
| T-328 | Create Chat page component structure | [x] | T-327 |
| T-329 | Build message display component | [x] | T-328 |
| T-330 | Build message input component | [x] | T-328 |
| T-331 | Implement API client for chat endpoint | [x] | T-330 |
| T-332 | Add real-time message updates and loading states | [x] | T-331 |
| T-333 | Integrate chat UI with task list | [x] | T-332 |

### Detailed Task Definitions

**T-328: Create Chat page component structure**

- **Description**: Build Chat page layout in `frontend/pages/chat.tsx` or `frontend/app/chat/page.tsx`
- **Acceptance Criteria**:
  - Page component created with proper Next.js structure
  - Layout includes: header, conversation list (sidebar), chat area, message input
  - Conversation list shows recent conversations with titles
  - Chat area is primary focus (responsive layout)
  - Mobile responsive: stacks conversation list on smaller screens
  - Protected route (requires authentication via Better Auth)
  - Redirects to login if not authenticated
  - Loads user's conversations on page mount
  - Conversation context/state initialized
  - No console errors on page load
- **Files**: `frontend/pages/chat.tsx` or `frontend/app/chat/page.tsx`
- **References**: [plan.md: Frontend Architecture], [spec.md: Chat UI]

---

**T-329: Build message display component**

- **Description**: Create MessageList component showing conversation messages
- **Acceptance Criteria**:
  - Component `MessageList` in `frontend/components/chat/MessageList.tsx`
  - Props: `messages: Message[], loading: boolean`
  - Each message displays: avatar (user/bot), role indicator, content, timestamp
  - User messages aligned right, assistant messages aligned left
  - Shows loading indicator while agent is responding
  - Scrolls to bottom automatically on new message
  - Timestamps formatted human-readable (e.g., "2 minutes ago")
  - Tool calls displayed when present (e.g., "✓ Added task: buy milk")
  - Handles long messages with text wrapping
  - Handles markdown or simple formatting in content
  - Empty state message if no messages yet
- **Files**: `frontend/components/chat/MessageList.tsx`
- **References**: [plan.md: Chat Components]

---

**T-330: Build message input component**

- **Description**: Create ChatInput component for user message entry
- **Acceptance Criteria**:
  - Component `ChatInput` in `frontend/components/chat/ChatInput.tsx`
  - Props: `onSubmit: (message: string) => void, loading: boolean`
  - Text input field with placeholder: "Type a message..."
  - Submit button (icon or text) to send message
  - Enter key sends message (Shift+Enter for newline)
  - Input disabled while loading
  - Input cleared after successful send
  - Shows character count (e.g., "1/5000")
  - Prevents empty message submission
  - Prevents message > 5000 characters
  - Focus input on mount and after send
  - Mobile-friendly (large touch targets)
- **Files**: `frontend/components/chat/ChatInput.tsx`
- **References**: [plan.md: Chat Components], [spec.md: FR-306-FR-309]

---

**T-331: Implement API client for chat endpoint**

- **Description**: Create chat API client in `frontend/lib/api/chat-client.ts`
- **Acceptance Criteria**:
  - Function `sendMessage(user_id: string, message: string, conversation_id?: string) → Promise<ChatResponse>`
  - Calls POST `/api/{user_id}/chat` with JWT token in Authorization header
  - Request body: `{message, conversation_id?}`
  - Returns parsed response with all fields: id, conversation_id, content, tool_calls, created_at
  - Handles errors: 400, 401, 403, 404, 500 with appropriate error messages
  - Automatically includes JWT token from authentication context
  - Implements timeout handling (30 second timeout)
  - Implements retry logic for transient errors
  - Logs requests/responses for debugging
  - Type-safe with TypeScript interfaces
  - No exposed API secrets or user data in logs
- **Files**: `frontend/lib/api/chat-client.ts`
- **References**: [spec.md: FR-306-FR-307], [plan.md: API Integration]

---

**T-332: Add real-time message updates and loading states**

- **Description**: Implement message state management and UI feedback
- **Acceptance Criteria**:
  - State management: `messages` (array), `loading` (boolean), `error` (string | null)
  - On message send: immediately add user message to UI (optimistic update)
  - Set `loading=true` while waiting for agent response
  - On agent response: add assistant message to UI
  - Set `loading=false` when response received
  - Show loading spinner while agent is processing
  - Display error message if send fails, with retry option
  - Auto-dismiss error after 5 seconds
  - Conversation persists across page navigation
  - Refresh conversation from database on page load
  - Handle network errors gracefully
  - No duplicate messages if retry happens
- **Files**: `frontend/pages/chat.tsx` or `frontend/app/chat/page.tsx`
- **References**: [plan.md: State Management], [spec.md: FR-339-FR-343]

---

**T-333: Integrate chat UI with task list**

- **Description**: Connect chat messages to main task list for real-time updates
- **Acceptance Criteria**:
  - When add_task called: new task appears in task list immediately
  - When complete_task called: task marked complete in list
  - When delete_task called: task removed from list
  - When update_task called: task details updated in list
  - Task list updates without page refresh
  - Chat shows task ID and title for reference in response
  - User can click task in chat message to navigate to detail view (optional)
  - Conversation list linked to tasks page
  - Both pages share same task data (consistent state)
  - Navigation between chat and tasks maintains scroll position
- **Files**: `frontend/pages/chat.tsx`, `frontend/components/chat/*.tsx`
- **References**: [plan.md: Integration], [spec.md: User Stories]

---

## Phase E: Testing & Deployment (T-334 to T-337)

**Goal**: Comprehensive testing and production deployment

| Task ID | Title | Status | Dependency |
|---------|-------|--------|------------|
| T-334 | Integration testing: all user stories | [ ] | T-333 |
| T-335 | Performance testing and optimization | [ ] | T-334 |
| T-336 | Security audit and penetration testing | [ ] | T-335 |
| T-337 | Deploy to production and monitor | [ ] | T-336 |

### Detailed Task Definitions

**T-334: Integration testing: all user stories**

- **Description**: End-to-end testing of all 6 user stories
- **Acceptance Criteria**:
  - **US1 - Add Task**: User sends "Add buy milk" → task created → appears in list. ✓
  - **US2 - List Tasks**: User sends "Show pending tasks" → all pending tasks listed. ✓
  - **US3 - Complete Task**: User sends "Mark task 1 done" → task marked complete. ✓
  - **US4 - Update Task**: User sends "Change task 1 to 'buy milk and bread'" → title updated. ✓
  - **US5 - Delete Task**: User sends "Delete task 2" → agent asks confirmation → task deleted. ✓
  - **US6 - Ambiguous Input**: User sends "Add milk and complete the list" → agent asks clarification. ✓
  - All edge cases tested: invalid task IDs, non-existent tasks, cross-user access attempts
  - All error scenarios tested: network failures, database errors, auth failures
  - Test suite: `backend/tests/test_integration_all_stories.py`
  - All tests passing: `pytest backend/tests/test_integration_all_stories.py -v`
  - Documentation of test results in `TESTING.md`
- **Files**: `backend/tests/test_integration_all_stories.py`, `TESTING.md`
- **References**: [spec.md: All User Stories], [plan.md: Testing]

---

**T-335: Performance testing and optimization**

- **Description**: Test system performance under load and optimize bottlenecks
- **Acceptance Criteria**:
  - Chat endpoint responds in < 2 seconds for normal messages
  - MCP tools respond in < 500ms for database operations
  - Conversation history load (20 messages) in < 100ms
  - Frontend loads chat page in < 1 second
  - Message input/output latency < 3 seconds end-to-end
  - Load test: 10 concurrent users, 100 messages each → no errors
  - Database queries use indexes (verified with EXPLAIN)
  - No N+1 queries in conversation history fetch
  - Frontend bundle size < 500KB (gzip)
  - Mobile performance acceptable (Lighthouse score > 85)
  - Performance test script: `backend/tests/test_performance.py`
  - Results documented in `PERFORMANCE.md`
- **Files**: `backend/tests/test_performance.py`, `PERFORMANCE.md`
- **References**: [plan.md: Performance]

---

**T-336: Security audit and penetration testing**

- **Description**: Security review and testing for vulnerabilities
- **Acceptance Criteria**:
  - **Authentication**: Verify JWT validation on all endpoints (401 on invalid token)
  - **Authorization**: Verify user isolation (user A cannot access user B's data)
  - **Injection**: Attempt SQL injection via message, title, description fields → all sanitized
  - **XSS**: Attempt XSS via message content → properly escaped in UI
  - **CSRF**: Verify token validation on POST requests
  - **Rate Limiting**: Test for DoS protection (optional: implement if missing)
  - **Secrets**: Verify no sensitive data in logs, error messages, or responses
  - **HTTPS**: Verify all endpoints use HTTPS in production
  - **CORS**: Verify CORS headers are properly configured
  - **Dependency Scanning**: Run `pip audit` and `npm audit` for known vulnerabilities
  - Security test results in `SECURITY.md`
  - All high/medium vulnerabilities resolved before deployment
- **Files**: `SECURITY.md`
- **References**: [plan.md: Security], [spec.md: FR-337]

---

**T-337: Deploy to production and monitor**

- **Description**: Deploy Phase III to production and set up monitoring
- **Acceptance Criteria**:
  - Backend deployed to production environment (Railway/AWS/similar)
  - Frontend deployed to Vercel with environment variables configured
  - Database migrations applied to production Neon database
  - Environment variables set: OPENAI_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET, etc.
  - Health check endpoint responds 200 OK
  - Monitoring configured: error logs, slow query alerts, uptime monitoring
  - Smoke tests run post-deployment: create task, list tasks, complete task
  - User-facing documentation updated with chat feature
  - Deployment process documented in `DEPLOYMENT.md`
  - Rollback plan in place
  - No errors in production logs for first 24 hours
  - All user stories confirmed working in production environment
- **Files**: `DEPLOYMENT.md`, deployment configuration files
- **References**: [plan.md: Deployment], [CLAUDE.md: Command Reference]

---

## Dependency Graph

```
Phase A (Database & Models): T-301 → T-302 → T-303 → T-304 → T-305
                                         ↓
Phase B (MCP Server): T-306 → T-307,T-308,T-309,T-310,T-311 → T-312 → T-313 → T-314 → T-315 → T-316 → T-317,T-318,T-319,T-320
                         ↓
Phase C (Agent & Endpoint): T-321 → T-322 → T-323 → T-324 → T-325 → T-326 → T-327
                              ↓
Phase D (Frontend): T-328 → T-329, T-330 → T-331 → T-332 → T-333
                      ↓
Phase E (Testing & Deployment): T-334 → T-335 → T-336 → T-337
```

---

## Parallel Execution Opportunities

### Within Phase A (Database)
- T-303 and T-304 can run in parallel (independent migrations)

### Within Phase B (MCP Tools)
- T-307-T-311 (5 tools) can be implemented in parallel after T-306
- T-317-T-320 (tool tests) can run in parallel

### Within Phase D (Frontend)
- T-329 and T-330 can be implemented in parallel
- UI components independent until integration in T-331-T-333

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
Complete **Phase A through Phase C** to deliver core functionality:
- Database schema and models (T-301 to T-305)
- 5 MCP tools fully functional (T-306 to T-320)
- Chat endpoint with JWT auth (T-321 to T-327)

This enables Users to manage tasks via natural language conversation.

### Phase 2 Scope (Full Feature)
Add **Phase D** for production-ready UI:
- Chat interface (T-328 to T-333)
- Integration with existing task list

### Phase 3 Scope (Production Ready)
Complete **Phase E** for deployment:
- Integration testing (T-334)
- Performance optimization (T-335)
- Security audit (T-336)
- Production deployment (T-337)

---

## Quick Start Checklist

- [ ] Review spec.md and plan.md
- [ ] Set up Neon database connection
- [ ] Run Phase A migrations
- [ ] Implement Phase B tools (start with T-306-T-311)
- [ ] Test tools manually (T-317-T-320)
- [ ] Implement Phase C agent and endpoint (T-321-T-327)
- [ ] End-to-end test complete flow (T-327)
- [ ] Build Phase D UI (T-328-T-333)
- [ ] Run integration tests (T-334)
- [ ] Deploy to production (T-337)

---

**Last Updated**: 2026-01-13
**Status**: Ready for Implementation
**Next Step**: Begin Phase A - Database & Models
