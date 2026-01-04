# Full-Stack Todo Application Constitution
<!-- Phase 2: Production-Ready Multi-User Web Application -->

## Core Principles

### I. Security First (NON-NEGOTIABLE)
- **Authentication Required**: All task operations require valid JWT authentication
- **User Isolation Enforced**: Users can only access their own data; backend validates user_id from JWT matches path user_id on every request
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
- **Schema Design**: Normalized tables; Clear foreign key relationships; NOT NULL constraints where appropriate; Unique constraints for natural keys (email); Indexes on frequently queried fields (user_id)
- **Data Integrity**: Foreign key constraints enforced; Validation in application layer (SQLModel + Pydantic); Transactions for multi-step operations; Cascade deletes where appropriate (user deleted → tasks deleted)
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

## Technology Stack

### Frontend Stack
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth (client)
- **State**: React hooks (useState, useEffect, useCallback, useMemo)
- **HTTP Client**: Fetch API (built-in)
- **Deployment**: Vercel

### Backend Stack
- **Framework**: FastAPI (async/await)
- **Language**: Python 3.13+ (type hints)
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT verification (shared secret with Better Auth)
- **Validation**: Pydantic models
- **Deployment**: Local (Phase 2) or Railway/Render/Fly.io (optional)

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
- **Optimized Images**: Next.js Image component
- **Code Splitting**: Automatic with App Router

### Backend Performance
- **API Response Time**: <500ms (P95)
- **Database Queries**: <100ms
- **Efficient Indexes**: On user_id (foreign key) and frequently queried fields
- **No N+1 Queries**: Use proper joins/eager loading
- **Connection Pooling**: Enabled

## Security Requirements (Phase 2)

### Authentication Security
✓ All passwords hashed (bcrypt via Better Auth)
✓ JWT tokens cryptographically signed with BETTER_AUTH_SECRET
✓ Tokens stored in httpOnly cookies (not localStorage/sessionStorage)
✓ Token expiration enforced (7 days default)
✓ User isolation enforced on every API request

### Input Validation
✓ All inputs validated at frontend (UX feedback)
✓ All inputs validated at backend (security boundary)
✓ Pydantic models for request validation
✓ SQL injection prevented (ORM usage)
✓ XSS prevented (React escaping)

### Data Protection
✓ User data isolated (user_id validation)
✓ CORS configured correctly
✓ No sensitive data exposed to client
✓ All secrets in environment variables
✓ HTTPS in production

## API Endpoint Standards

### Endpoint Structure
- **Base Path**: /api
- **User-Scoped Resources**: /api/{user_id}/tasks
- **Authentication**: All task endpoints require Authorization: Bearer <token>
- **User Validation**: Backend verifies token user_id matches path user_id

### Standard Task Endpoints
- `GET /api/{user_id}/tasks` - List all user's tasks
- `POST /api/{user_id}/tasks` - Create new task (body: {title, description?})
- `GET /api/{user_id}/tasks/{id}` - Get specific task
- `PUT /api/{user_id}/tasks/{id}` - Update task (body: {title, description?})
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion status

### Request/Response Format
- **Request Headers**: Content-Type: application/json, Authorization: Bearer <token>
- **Request Body**: Valid JSON matching Pydantic model
- **Response Success**: JSON object or array (not wrapped)
- **Response Error**: {"detail": "error message"}
- **CORS**: Allow origin from FRONTEND_URL env var; allow credentials; allow GET, POST, PUT, DELETE, PATCH

## Data Models

### User Model (Managed by Better Auth)
```typescript
interface User {
  id: string;          // UUID
  email: string;       // Unique
  name: string;
  password_hash: string;
  created_at: string;  // ISO timestamp
}
```

### Task Model
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

### SQLModel Schema
```python
# models.py
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
```

## Business Rules

### Task Operations
- Users can only access their own tasks (enforced in backend via JWT user_id validation)
- Task IDs auto-increment (PostgreSQL SERIAL)
- Completed tasks can be toggled back to pending
- Deleted tasks cannot be recovered (no soft delete in Phase 2)
- Each user has independent task list
- Empty task list shows helpful empty state (frontend)

### Validation Rules
- **Title**: Required, 1-200 characters, non-empty after trim
- **Description**: Optional, max 1000 characters
- **Completed**: Boolean, defaults to false
- **User ID**: Must match JWT token user_id

## Development Workflow

### Environment Setup
- **Frontend .env.local**:
  ```
  BETTER_AUTH_SECRET=<shared-secret-32-chars-min>
  BETTER_AUTH_URL=http://localhost:3000
  BACKEND_URL=http://localhost:8000
  ```
- **Backend .env**:
  ```
  BETTER_AUTH_SECRET=<same-shared-secret>
  DATABASE_URL=<neon-connection-string>
  FRONTEND_URL=http://localhost:3000
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
│   ├── lib/               # Utilities (api.ts, types.ts)
│   ├── public/            # Static assets
│   ├── .env.local         # Frontend environment
│   └── package.json
├── backend/
│   ├── main.py            # FastAPI app
│   ├── models.py          # SQLModel schemas
│   ├── auth.py            # JWT verification
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

### Backend Deployment (Phase 2: Optional)
- **Development**: Can run locally for Phase 2
- **Production Options**: Railway, Render, Fly.io, or similar
- **Environment Variables**: Configured in platform dashboard
- **CORS**: Update with production frontend URL

### Database (Neon)
- **Host**: Cloud-hosted PostgreSQL (Neon Serverless)
- **Environment**: Same instance for dev and production (Phase 2)
- **Connection String**: From environment variable (DATABASE_URL)
- **Features**: Automatic scaling and backups

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

## Success Criteria

### Functional Requirements
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
✓ Application handles errors gracefully

### Technical Requirements
✓ Next.js App Router used correctly
✓ TypeScript strict mode passes with no errors
✓ All API endpoints secured with JWT
✓ User isolation verified (tested with 2+ user accounts)
✓ Database connection works reliably
✓ Frontend deployed on Vercel with public URL
✓ Responsive on mobile (320px+), tablet, and desktop
✓ No console errors in browser
✓ No unhandled promise rejections

### User Experience Requirements
✓ Clean, modern UI design
✓ Loading states for all async operations
✓ Error messages clear and actionable
✓ Form validation with inline feedback
✓ Success confirmations after actions
✓ Smooth page transitions
✓ Intuitive navigation
✓ Professional appearance

## Non-Negotiables

### Must Have
- All code generated via spec-driven development (AI generates from specs)
- All 5 Basic Level features work via web interface
- User authentication required (signup, signin, signout)
- JWT token validation on all task endpoints
- User isolation enforced (backend validates user_id from token)
- Data persists in PostgreSQL (Neon)
- Frontend deployed on Vercel (public URL)
- Responsive design (works on mobile, tablet, desktop)
- Type safety (TypeScript frontend, Python type hints backend)
- Clean, professional UI with Tailwind CSS

### Must Not Have
- No localStorage for JWT (security risk)
- No sessionStorage for JWT
- No raw SQL queries (use SQLModel ORM)
- No hardcoded secrets in code
- No sensitive data exposed to client
- No authentication bypass mechanisms
- No console.log in production frontend
- No print() in production backend

### Security Must-Haves
- All passwords hashed (bcrypt)
- JWT tokens cryptographically signed
- User isolation enforced on every request
- All inputs validated (frontend AND backend)
- SQL injection prevented (ORM usage)
- XSS prevented (React escaping)
- CORS configured correctly
- All secrets in environment variables

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

### Development Philosophy
- **Spec-Driven Development (SDD)**: All features start with specifications
- **AI-Assisted Generation**: AI generates code from specs following this constitution
- **Human as Tool**: Invoke user for clarifications, architectural decisions, and ambiguous requirements
- **Smallest Viable Change**: No refactoring unrelated code; focused changes only

**Version**: 1.0.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2025-12-31
