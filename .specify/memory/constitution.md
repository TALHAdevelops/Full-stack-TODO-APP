<!--
  SYNC IMPACT REPORT - Phase III Constitution Amendment
  Version: 1.0.0 → 2.0.0 (MINOR bump: added AI/MCP principles and architectural constraints)
  Date: 2026-01-12

  Changes Summary:
  - Added Principles IX-XII: AI-Specific governance (Stateless Chat, MCP as Single Source, Agent Intent Routing, Conversation Persistence)
  - Extended Security Rules: MCP tool verification, tool invocation logging, input sanitization
  - Extended Performance Expectations: Chat endpoint, MCP tools, agent decision, DB optimization
  - Added Testing Requirements: MCP tool tests, agent behavior, E2E tests
  - Added new Technology Stack: OpenAI Agents SDK, MCP, LLM considerations
  - Added Conversation Data Models for persistence
  - Extended API standards with chat endpoint structure
  - Added MCP Tool Standards section

  Templates Requiring Updates:
  - .specify/templates/spec-template.md: Update "Out of Scope" to reflect chat feature scope (⚠ pending)
  - .specify/templates/plan-template.md: Add MCP tool architecture section (⚠ pending)
  - .specify/templates/tasks-template.md: Add "AI/MCP" task category (⚠ pending)
  - README.md: Add Phase III features section (⚠ pending)

  Deferred Items: None
-->

# Full-Stack Todo Application Constitution - Phase III Extension

<!-- Phase 2: Production-Ready Multi-User Web Application -->
<!-- Phase 3: AI-Powered Conversational Interface with MCP Integration -->

## Core Principles

### I. Security First (NON-NEGOTIABLE)
- **Authentication Required**: All task operations and chat interactions require valid JWT authentication
- **User Isolation Enforced**: Users can only access their own data and conversations; backend validates user_id from JWT matches path user_id on every request
- **Zero Trust**: All inputs validated at API boundary (frontend AND backend); SQL injection prevented via ORM; XSS prevented via React escaping
- **Secrets Management**: All secrets in environment variables (.env files); Never hardcoded; .gitignore excludes all .env files
- **Password Security**: All passwords hashed via bcrypt (Better Auth handles); No passwords in logs; JWT tokens in httpOnly cookies only
- **CORS Configured**: Allow specific frontend origin only; credentials enabled; proper methods and headers whitelisted

### II. Type Safety Mandatory
- **Frontend TypeScript Strict Mode**: No 'any' types unless absolutely necessary; All props, functions, API responses typed; Exhaustive type checking
- **Backend Python Type Hints**: All function parameters and returns typed; Pydantic models for all request/response validation
- **Database Type Safety**: SQLModel ORM combines SQLAlchemy + Pydantic; No raw SQL queries; Type-safe queries throughout

### III. API-First Architecture
- **Clean Separation**: Frontend (Next.js) and backend (FastAPI) are independent services; communicate via REST API only
- **Stateless Backend**: JWT-based authentication; no server sessions; horizontal scaling ready
- **RESTful Conventions**: GET (read), POST (create), PUT (update), DELETE (delete), PATCH (partial); Consistent endpoint structure: /api/{user_id}/{resource}
- **Proper HTTP Status Codes**: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error
- **Consistent Response Format**: JSON always; Success returns resource/list; Error returns {"detail": "message"}

### IV. Modern Frontend Standards (Next.js 16+)
- **App Router Only**: File-based routing in app/ directory; Server Components by default; Client Components only when needed ('use client' directive)
- **Tailwind CSS Only**: Utility classes exclusively; No custom CSS files; No inline styles (except dynamic values); Mobile-first responsive design
- **Component Architecture**: Reusable UI in components/ui/; Feature components in components/[feature]/; Single responsibility per component
- **State Management**: React hooks for local state; Server Components for server state; No global state library in Phase 2
- **Centralized API Client**: All backend calls through lib/api.ts; Consistent error handling; Loading states for all async operations

### V. Database Best Practices (SQLModel + PostgreSQL)
- **ORM Required**: SQLModel for all database operations; No raw SQL queries allowed
- **Schema Design**: Normalized tables; Clear foreign key relationships; NOT NULL constraints where appropriate; Unique constraints for natural keys (email); Indexes on frequently queried fields (user_id, conversation_id)
- **Data Integrity**: Foreign key constraints enforced; Validation in application layer (SQLModel + Pydantic); Transactions for multi-step operations; Cascade deletes where appropriate (user deleted → tasks/conversations deleted)
- **Connection Management**: Neon Serverless PostgreSQL; Connection pooling enabled; pool_pre_ping=True for health checks; Connection string from environment variable

### VI. Authentication & JWT Flow (Better Auth)
- **Better Auth Library**: JWT plugin enabled; Token expiration: 7 days (configurable); Secure password hashing (bcrypt); Email validation
- **JWT Token Flow**: Better Auth issues JWT on login → Stored in httpOnly cookies → Sent in Authorization: Bearer <token> header → Backend verifies JWT signature with shared secret → Extract user_id from token payload (sub claim) → Validate user_id in URL matches token user_id
- **Shared Secret**: BETTER_AUTH_SECRET environment variable; Same secret in frontend and backend; Minimum 32 characters; Random, cryptographically secure; Never hardcoded

### VII. Error Handling Philosophy
- **Frontend Error Strategy**: Network errors: helpful message; 401 errors: redirect to login; 404: resource not found; 422: inline validation messages; 500: generic error; Toast notifications for success/error feedback; Loading states prevent duplicate submissions
- **Backend Error Strategy**: HTTPException for expected errors with proper status codes; Descriptive error messages; Exception handlers for unexpected errors; Never expose internal errors/stack traces to client; Log all errors for debugging

### VIII. Code Quality Standards
- **General Principles**: DRY (Don't Repeat Yourself); KISS (Keep It Simple, Stupid); Single Responsibility Principle; Consistent naming conventions; Self-documenting code
- **Avoid Over-Engineering**: Only make changes directly requested or clearly necessary; Keep solutions simple and focused; No premature abstractions; Don't add features, refactoring, or "improvements" beyond what was asked
- **No Unnecessary Comments**: Don't add docstrings, comments, or type annotations to code you didn't change; Only add comments where logic isn't self-evident; Code should be self-documenting via clear naming

### IX. Stateless Chat Architecture (Phase III)
- **No Server-Side Session Memory**: Chat endpoint does not maintain user conversation state between requests
- **Conversation History in Database**: All conversation history stored in Conversation and Message tables; Each request includes full context needed for agent decision-making
- **Agent is Ephemeral**: OpenAI Agent SDK instantiated fresh for each chat request; No persistent agent state across requests
- **Context Passing**: User message + conversation history retrieved from DB → passed to agent → agent executes MCP tools → response stored in DB → returned to client

### X. MCP as Single Source of Truth (Phase III)
- **No Direct Database Access from Chat**: Chat endpoint cannot query database directly; all data access MUST go through MCP tools
- **MCP Tools are Gatekeepers**: Tasks, conversations, and user data accessed only via MCP tools; agent invokes tools, tools verify permissions, tools perform DB operations
- **Tool Execution Isolation**: Each MCP tool execution is independent; tools verify user_id before every operation; tools handle all Pydantic validation and error handling
- **Tool Response Logging**: Every tool invocation logged with user_id, timestamp, tool name, input, and result; enables auditing and debugging

### XI. Agent Intent Routing (Phase III)
- **OpenAI Agent SDK**: Structured reasoning determines whether message requires task action or pure conversation
- **Intent Types**: Create task, read tasks, update task, delete task, toggle task, chat/clarify
- **Tool Selection Discipline**: Agent uses minimal tool set for current intent; no speculative tool calls; agent reasons about next step based on tool results
- **Error Recovery**: Agent retries tool calls with adjusted parameters on recoverable errors; escalates to user with clear explanation on persistent failures

### XII. Conversation Persistence (Phase III)
- **Immutable Message History**: Each user message and agent response stored as Message records; never deleted (soft delete only if audit required)
- **Thread Integrity**: Conversation records group related messages; clear relationship between conversations and tasks mentioned
- **Search & Recall**: Conversation history indexed for user to review past interactions; enables multi-turn context retention without server session

## Technology Stack

### Frontend Stack
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth (client)
- **State**: React hooks (useState, useEffect, useCallback, useMemo)
- **HTTP Client**: Fetch API (built-in)
- **Chat UI Kit**: OpenAI ChatKit (TypeScript)
- **Deployment**: Vercel

### Backend Stack
- **Framework**: FastAPI (async/await)
- **Language**: Python 3.13+ (type hints)
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT verification (shared secret with Better Auth)
- **Validation**: Pydantic models
- **AI Agent Framework**: OpenAI Agents SDK (Python)
- **MCP Protocol**: Model Context Protocol (server-side MCP implementation)
- **LLM**: OpenAI API (gpt-4o or latest reasoning model)
- **Deployment**: Local (Phase 3) or Railway/Render/Fly.io (optional)

### Development Tools
- **Package Managers**: npm (frontend), pip/uv (backend)
- **Environment Files**: .env.local (frontend), .env (backend)
- **Version Control**: Git + GitHub
- **Code Organization**: Separate frontend/ and backend/ folders

## Styling Standards

### Tailwind CSS Guidelines
- **Color Palette**:
  - Primary: blue-600
  - Secondary: purple-600
  - Success: green-600
  - Warning: yellow-600
  - Error: red-600
  - Neutral: gray-100 to gray-900
- **Spacing Scale**: Consistent use of px-4, py-2, gap-4, etc.
- **Responsive Design**: Mobile-first approach (min-width breakpoints)
- **No Custom CSS**: All styling via Tailwind utility classes
- **No Inline Styles**: Except for truly dynamic values (e.g., dynamic colors, positions)

## Performance Requirements

### Frontend Performance
- **Initial Page Load**: <2 seconds
- **Time to Interactive**: <3 seconds
- **Lighthouse Score**: >80
- **Chat UI Response**: <500ms (local rendering)
- **Optimized Images**: Next.js Image component
- **Code Splitting**: Automatic with App Router

### Backend Performance
- **API Response Time**: <500ms (P95)
- **Chat Endpoint Response**: <5 seconds (including agent execution)
- **MCP Tool Execution**: <2 seconds per tool
- **Agent Decision Time**: <1 second (intent routing + tool selection)
- **Database Queries**: <100ms
- **Efficient Indexes**: On user_id (foreign key), conversation_id, and frequently queried fields
- **No N+1 Queries**: Use proper joins/eager loading
- **Connection Pooling**: Enabled

## Security Requirements (Phase 2 + Phase 3 Extensions)

### Authentication Security
✓ All passwords hashed (bcrypt via Better Auth)
✓ JWT tokens cryptographically signed with BETTER_AUTH_SECRET
✓ Tokens stored in httpOnly cookies (not localStorage/sessionStorage)
✓ Token expiration enforced (7 days default)
✓ User isolation enforced on every API request
✓ Chat endpoint requires JWT auth (same as task endpoints)

### Input Validation
✓ All inputs validated at frontend (UX feedback)
✓ All inputs validated at backend (security boundary)
✓ Pydantic models for request validation
✓ SQL injection prevented (ORM usage)
✓ XSS prevented (React escaping)
✓ Natural language input sanitized (no injection attacks via chat)

### Data Protection
✓ User data isolated (user_id validation)
✓ CORS configured correctly
✓ No sensitive data exposed to client
✓ All secrets in environment variables
✓ HTTPS in production
✓ MCP tools verify user_id before any DB access
✓ Agent cannot access raw database (only through MCP tools)

### MCP Tool Security (Phase III)
✓ Tool invocations logged with user_id, timestamp, tool name, input, result
✓ Each tool verifies user_id before executing (inherited from Phase II patterns)
✓ Tool errors captured and logged without exposing internal details
✓ Tool response validation ensures safety before agent uses result

## API Endpoint Standards

### Phase II: Task Management Endpoints
- **Base Path**: /api
- **User-Scoped Resources**: /api/{user_id}/tasks
- **Authentication**: All endpoints require Authorization: Bearer <token>
- **User Validation**: Backend verifies token user_id matches path user_id

#### Task Endpoints
- `GET /api/{user_id}/tasks` - List all user's tasks
- `POST /api/{user_id}/tasks` - Create new task (body: {title, description?})
- `GET /api/{user_id}/tasks/{id}` - Get specific task
- `PUT /api/{user_id}/tasks/{id}` - Update task (body: {title, description?})
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion status

### Phase III: Chat Endpoints (New)
- **Base Path**: /api/chat
- **Chat Request**: `POST /api/{user_id}/chat` - Send message to AI agent
  - **Request Body**:
    ```json
    {
      "message": "string (user query)",
      "conversation_id": "string (optional, for continuing existing conversation)"
    }
    ```
  - **Response**:
    ```json
    {
      "id": "string (message id)",
      "conversation_id": "string",
      "user_id": "string",
      "content": "string (agent response)",
      "tool_calls": [{"tool_name": "string", "args": {...}, "result": {...}}],
      "created_at": "ISO timestamp"
    }
    ```

- **Retrieve Conversations**: `GET /api/{user_id}/conversations` - List user's conversations
- **Retrieve Conversation History**: `GET /api/{user_id}/conversations/{conversation_id}/messages` - Get all messages in conversation

### Request/Response Format
- **Request Headers**: Content-Type: application/json, Authorization: Bearer <token>
- **Request Body**: Valid JSON matching Pydantic model
- **Response Success**: JSON object or array (not wrapped)
- **Response Error**: {"detail": "error message"}
- **CORS**: Allow origin from FRONTEND_URL env var; allow credentials; allow GET, POST, PUT, DELETE, PATCH

## MCP Tool Standards (Phase III)

### Tool Definition Requirements
- **Type Hints**: All parameters and return types explicitly typed
- **Validation**: Pydantic model for input parameters; validates before tool execution
- **User Verification**: Every tool checks user_id from JWT token before accessing user data
- **Error Handling**: Descriptive error messages; never expose internal database errors
- **Logging**: Tool invocation logged (user_id, timestamp, tool name, input, result)

### Tool Categories
1. **Task Management Tools**:
   - `create_task(user_id, title, description?)` → Task
   - `list_tasks(user_id)` → List[Task]
   - `get_task(user_id, task_id)` → Task
   - `update_task(user_id, task_id, title?, description?)` → Task
   - `delete_task(user_id, task_id)` → Success
   - `toggle_task(user_id, task_id)` → Task

2. **Conversation Management Tools**:
   - `get_conversation_history(user_id, conversation_id, limit=50)` → List[Message]
   - `create_conversation(user_id, title?)` → Conversation
   - All tools follow Phase II patterns (Pydantic validation, user_id verification)

### Tool Response Contract
- **Success**: Returns typed object or array matching expected schema
- **Validation Error** (400): Descriptive message about invalid parameters
- **Permission Error** (403): "User not authorized to access this resource"
- **Not Found** (404): "Resource not found"
- **Server Error** (500): Generic message; internal error logged separately

## Data Models

### Phase II: User Model (Managed by Better Auth)
```typescript
interface User {
  id: string;          // UUID
  email: string;       // Unique
  name: string;
  password_hash: string;
  created_at: string;  // ISO timestamp
}
```

### Phase II: Task Model
```typescript
interface Task {
  id: number;          // Auto-increment (PostgreSQL SERIAL)
  user_id: string;     // Foreign key to users.id
  title: string;       // 1-200 characters, required
  description: string | null; // Max 1000 characters, optional
  completed: boolean;  // Default: false
  created_at: string;  // Auto-generated ISO timestamp
  updated_at: string;  // Auto-updated ISO timestamp
}
```

### Phase III: Conversation Model (New)
```typescript
interface Conversation {
  id: string;          // UUID
  user_id: string;     // Foreign key to users.id
  title: string;       // Auto-generated or user-provided summary
  created_at: string;  // ISO timestamp
  updated_at: string;  // ISO timestamp
}
```

### Phase III: Message Model (New)
```typescript
interface Message {
  id: string;          // UUID
  conversation_id: string; // Foreign key to conversations.id
  user_id: string;     // Foreign key to users.id
  role: "user" | "assistant"; // Who sent this message
  content: string;     // Message text
  tool_calls?: Array<{
    tool_name: string;
    input: object;
    result: object;
    executed_at: string;
  }>;
  created_at: string;  // ISO timestamp
}
```

### SQLModel Schema (Python Backend)
```python
# models.py - Phase II
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# models.py - Phase III (New)
import uuid

class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Message(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    role: str = Field(default="user")  # "user" or "assistant"
    content: str
    tool_calls: Optional[str] = Field(default=None)  # JSON-serialized
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Business Rules

### Phase II: Task Operations
- Users can only access their own tasks (enforced in backend via JWT user_id validation)
- Task IDs auto-increment (PostgreSQL SERIAL)
- Completed tasks can be toggled back to pending
- Deleted tasks cannot be recovered (no soft delete in Phase 2)
- Each user has independent task list
- Empty task list shows helpful empty state (frontend)

### Phase III: Chat Operations
- Chat is conversational; agent maintains context via conversation history in DB
- Each user message creates a new Message record
- Agent responses create assistant Message records
- Agent can invoke MCP tools to manage tasks
- Tool results logged in message.tool_calls for transparency
- Users can start multiple independent conversations
- Conversations are user-isolated (enforced in backend)

## Development Workflow

### Environment Setup
- **Frontend .env.local**:
  ```
  BETTER_AUTH_SECRET=<shared-secret-32-chars-min>
  BETTER_AUTH_URL=http://localhost:3000
  BACKEND_URL=http://localhost:8000
  OPENAI_API_KEY=<openai-api-key>
  ```
- **Backend .env**:
  ```
  BETTER_AUTH_SECRET=<same-shared-secret>
  DATABASE_URL=<neon-connection-string>
  FRONTEND_URL=http://localhost:3000
  OPENAI_API_KEY=<openai-api-key>
  ```
- **.env.example files**: Template with placeholders (no secrets)
- **.gitignore**: Excludes .env, .env.local, .env.*

### Local Development
- **Frontend**: `npm run dev` (localhost:3000)
- **Backend**: `uvicorn main:app --reload` (localhost:8000)
- **Database**: Neon cloud (no local PostgreSQL needed)
- **Testing**: Use multiple browser profiles to test user isolation

### Code Organization
```
project-root/
├── frontend/
│   ├── app/               # Next.js App Router
│   ├── components/        # React components
│   │   ├── ui/           # Shared UI components
│   │   └── chat/         # Chat-specific components (Phase III)
│   ├── lib/               # Utilities (api.ts, types.ts)
│   ├── public/            # Static assets
│   ├── .env.local         # Frontend environment
│   └── package.json
├── backend/
│   ├── main.py            # FastAPI app
│   ├── models.py          # SQLModel schemas
│   ├── auth.py            # JWT verification
│   ├── mcp_tools.py       # MCP tool implementations (Phase III)
│   ├── chat.py            # Chat endpoint logic (Phase III)
│   ├── .env               # Backend environment
│   └── requirements.txt
├── specs/                 # Feature specifications
├── .specify/              # SDD templates and scripts
└── README.md              # Setup instructions
```

## Deployment Standards

### Frontend Deployment (Vercel)
- **Platform**: Vercel (automatic deploys from GitHub)
- **Environment Variables**: Configured in Vercel dashboard
- **Build Command**: `npm run build`
- **Production URL**: https://your-app.vercel.app
- **CORS Update**: Update backend FRONTEND_URL to production URL

### Backend Deployment (Phase 2: Optional / Phase 3: Required)
- **Development**: Can run locally for Phase 2
- **Production**: Railway, Render, Fly.io, or similar
- **Environment Variables**: Configured in platform dashboard
- **CORS**: Update with production frontend URL
- **MCP Server**: Deployed alongside FastAPI (Phase III)

### Database (Neon)
- **Host**: Cloud-hosted PostgreSQL (Neon Serverless)
- **Environment**: Same instance for dev and production
- **Connection String**: From environment variable (DATABASE_URL)
- **Features**: Automatic scaling and backups
- **Phase III**: Indexes on conversation_id, user_id for chat performance

## Phase 2 Scope

### Must Have (Basic Level Features)
✓ User authentication (signup, signin, signout via Better Auth)
✓ JWT token validation on all task endpoints
✓ User isolation enforced (backend validates user_id)
✓ Add task (title + optional description)
✓ View all user's tasks (list)
✓ Edit task (title and/or description)
✓ Delete task
✓ Toggle task completion status (pending ↔ complete)
✓ Data persists in PostgreSQL (Neon)
✓ Frontend deployed on Vercel (public URL)
✓ Responsive design (mobile, tablet, desktop)
✓ Type safety (TypeScript frontend, Python backend)
✓ Clean, professional UI with Tailwind CSS
✓ Error handling with user feedback
✓ Loading states for async operations

### Out of Scope (Phase 2)
✗ Advanced features (priorities, tags, due dates, search, filter, sort)
✗ Real-time updates (WebSockets/SSE)
✗ Email verification
✗ Password reset flow
✗ Social login (Google, GitHub)
✗ Profile pages
✗ Task sharing between users
✗ File uploads
✗ Mobile native app
✗ Admin panel
✗ Analytics/metrics
✗ Internationalization (i18n)
✗ Dark mode (can add as bonus)
✗ Task categories/reminders/recurring tasks
✗ AI chat interface (Phase III)

## Phase 3 Scope

### Must Have (AI Chatbot Features)
✓ Natural language interface via OpenAI Agents SDK
✓ Conversational chat UI with message history
✓ Agent can understand and execute task operations
✓ Task management via natural language ("Create a task to...", "Mark task as done")
✓ Conversation history stored and retrievable
✓ MCP tools verify user_id before any DB access
✓ Chat endpoint requires JWT authentication
✓ Tool invocations logged with user_id, timestamp, result
✓ Agent responses include transparency on tool usage
✓ User isolation enforced (user only sees own conversations)

### Out of Scope (Phase 3)
✗ Voice input/output
✗ Multi-language support
✗ Advanced NLU (beyond OpenAI Agent capabilities)
✗ Task scheduling based on natural language
✗ Integration with external calendar/email systems
✗ Model fine-tuning or custom LLM
✗ Real-time streaming responses (MVP: request/response)
✗ Agent memory across sessions (unless via conversation history)

## Success Criteria

### Functional Requirements (Phase 2)
✓ Users can sign up with email/password
✓ Users can sign in and receive JWT token
✓ Users can sign out
✓ Users can add tasks (title + optional description)
✓ Users can view all their tasks
✓ Users can edit task title and/or description
✓ Users can delete tasks
✓ Users can toggle task status (pending ↔ complete)
✓ Users cannot see other users' tasks (isolation verified)
✓ Tasks persist after page refresh
✓ Tasks persist after server restart

### Functional Requirements (Phase 3)
✓ Users can chat with AI agent
✓ Agent understands task-related requests
✓ Agent can create, update, delete, and list tasks via natural language
✓ Conversation history persists and is retrievable
✓ Users cannot see other users' conversations
✓ Agent responses show which tools were used and their results
✓ Chat errors handled gracefully with helpful messages

### Technical Requirements (Phase 2)
✓ Next.js App Router used correctly
✓ TypeScript strict mode passes with no errors
✓ All API endpoints secured with JWT
✓ User isolation verified (tested with 2+ user accounts)
✓ Database connection works reliably
✓ Frontend deployed on Vercel with public URL
✓ Responsive on mobile (320px+), tablet, and desktop
✓ No console errors in browser
✓ No unhandled promise rejections

### Technical Requirements (Phase 3)
✓ OpenAI Agents SDK integrated correctly
✓ MCP tools implement type-safe operations
✓ MCP tools verify user_id on every operation
✓ Chat endpoint response time <5 seconds (P95)
✓ MCP tool execution <2 seconds per tool
✓ Agent decision time <1 second
✓ Conversation history correctly stored and retrieved
✓ Tool invocations logged to database
✓ TypeScript ChatKit integration has no 'any' types
✓ No Python exceptions leaked to chat endpoint

### User Experience Requirements (Phase 2)
✓ Clean, modern UI design
✓ Loading states for all async operations
✓ Error messages clear and actionable
✓ Form validation with inline feedback
✓ Success confirmations after actions
✓ Smooth page transitions
✓ Intuitive navigation
✓ Professional appearance

### User Experience Requirements (Phase 3)
✓ Chat interface is intuitive and responsive
✓ Agent responses are natural and helpful
✓ Tool usage is transparent (user knows what agent did)
✓ Error messages guide user to recovery
✓ Conversation history is easy to navigate
✓ No noticeable latency in agent responses
✓ Mobile-friendly chat UI

## Testing Requirements (Phase 3)

### MCP Tool Tests
- Unit tests for each MCP tool (create, read, update, delete, toggle tasks)
- User isolation verified: tool rejects user_id mismatch
- Error handling: tool returns proper error codes and messages
- Validation: invalid inputs rejected with descriptive error
- Database state: tool operations correctly persist to DB

### Agent Behavior Tests
- 15+ sample conversations tested end-to-end
- Agent correctly routes requests to appropriate tools
- Agent handles tool errors gracefully
- Agent generates natural, helpful responses
- Agent understands context from conversation history
- Multi-turn conversations maintain coherent context

### Chat Endpoint Tests
- JWT verification: rejected requests without valid token
- User isolation: user cannot access other user's conversations
- Conversation persistence: messages correctly stored and retrieved
- Performance: response time consistently <5 seconds
- Error handling: network errors, tool failures handled gracefully

### End-to-End Tests
- User signs up → chats → creates task → asks to list → agent provides list
- User starts conversation → asks to update task → agent updates → persists
- Two users isolated: user A cannot see user B's conversations
- Agent retries on recoverable tool failure
- Tool invocation logging: all operations auditable by user_id

## Non-Negotiables

### Must Have
- All code generated via spec-driven development (AI generates from specs)
- All Phase 2 features work via web interface
- All Phase 3 chat features work correctly
- User authentication required (signup, signin, signout)
- JWT token validation on all endpoints (tasks + chat)
- User isolation enforced on every request
- Data persists in PostgreSQL (Neon)
- Frontend deployed on Vercel (public URL)
- Responsive design (works on mobile, tablet, desktop)
- Type safety (TypeScript frontend, Python type hints backend)
- Clean, professional UI with Tailwind CSS
- MCP tools verify user_id before any DB access
- Chat endpoint requires JWT authentication
- Agent cannot access raw database (only via MCP tools)

### Must Not Have
- No localStorage for JWT (security risk)
- No sessionStorage for JWT
- No raw SQL queries (use SQLModel ORM)
- No hardcoded secrets in code
- No sensitive data exposed to client
- No authentication bypass mechanisms
- No console.log in production frontend
- No print() in production backend
- No direct database access from chat endpoint
- No tool invocations without logging
- No unvalidated natural language injection
- No MCP tools that skip user_id verification

### Security Must-Haves
- All passwords hashed (bcrypt)
- JWT tokens cryptographically signed
- User isolation enforced on every request
- All inputs validated (frontend AND backend)
- SQL injection prevented (ORM usage)
- XSS prevented (React escaping)
- CORS configured correctly
- All secrets in environment variables
- Chat input sanitized (no injection attacks)
- Tool invocations logged with user_id
- MCP tools enforce access control

## Governance

### Constitution Authority
- This constitution supersedes all other practices and guidelines
- All code, specs, and implementations must comply with these principles
- Amendments require documentation and approval via /sp.constitution
- CLAUDE.md provides runtime development guidance and must align with this constitution

### Compliance Verification
- All PRs/reviews must verify compliance with security, type safety, and API standards
- Complexity must be justified; simple solutions preferred
- Over-engineering is explicitly discouraged
- User isolation must be tested with multiple user accounts before deployment
- MCP tools must be verified to enforce user_id checks before deployment

### Development Philosophy
- **Spec-Driven Development (SDD)**: All features start with specifications
- **AI-Assisted Generation**: AI generates code from specs following this constitution
- **Human as Tool**: Invoke user for clarifications, architectural decisions, and ambiguous requirements
- **Smallest Viable Change**: No refactoring unrelated code; focused changes only

### Version Control
- **Semantic Versioning**: MAJOR.MINOR.PATCH
  - MAJOR: Backward incompatible principle changes or removals
  - MINOR: New principle/section added or materially expanded guidance
  - PATCH: Clarifications, wording, typo fixes, non-semantic refinements
- **Amendment Log**: Each amendment updates LAST_AMENDED_DATE and documents changes in Sync Impact Report comment

**Version**: 2.0.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2026-01-12
