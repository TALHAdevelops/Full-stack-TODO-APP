# Implementation Plan: TaskFlow Web Application

**Branch**: `2-taskflow-web-app` | **Date**: 2025-12-31 | **Spec**: [specs/2-taskflow-web-app/spec.md](specs/2-taskflow-web-app/spec.md)
**Input**: Feature specification for a multi-user web-based todo application with authentication and persistent storage.

## Summary

Build a production-ready, multi-user web application (TaskFlow Web) by transforming the Phase 1 console app into a modern full-stack system. The architecture consists of a Next.js 16+ frontend (App Router, Better Auth, Tailwind) and a FastAPI backend (Python 3.13+, SQLModel, JWT verification) backed by a Neon Serverless PostgreSQL database. This plan delivers 5 core CRUD features plus user authentication with strict user isolation and type safety.

## Technical Context

**Language/Version**: Python 3.13+ (Backend), TypeScript 5.x+ (Frontend)
**Primary Dependencies**: FastAPI, SQLModel, PyJWT, Pydantic-Settings (Backend); Next.js 16+, Better Auth, Tailwind CSS, React 19 (Frontend)
**Storage**: Neon Serverless PostgreSQL
**Testing**: Manual API testing (Postman/curl), Manual UI/Integration testing
**Target Platform**: Vercel (Frontend), Local/Railway/Render (Backend)
**Project Type**: Web application (Frontend + Backend)
**Performance Goals**: <2s initial load, <500ms API response (P95), <100ms DB queries
**Constraints**: <500ms p95 latency, mobile-first responsive design, strict user isolation
**Scale/Scope**: Multi-user support, 5 CRUD features + Authentication, Neon free tier (0.5GB)

## Constitution Check

| Principle | Check/Status |
|-----------|--------------|
| **Security First** | Verified: JWT auth, httpOnly cookies, user isolation enforced on every request |
| **Type Safety** | Verified: TypeScript strict mode (frontend) + Python type hints (backend) + SQLModel |
| **API-First** | Verified: Clean separation, RESTful conventions, stateless backend |
| **Modern Frontend** | Verified: Next.js 16 App Router, Tailwind CSS, Server/Client components |
| **Database Best Practices** | Verified: SQLModel ORM, Neon PostgreSQL, connection pooling, cascade deletes |
| **Code Quality** | Verified: DRY, KISS, no premature abstractions |

## Project Structure

### Documentation (this feature)

```text
specs/2-taskflow-web-app/
├── plan.md              # This file
├── spec.md              # Feature requirements
├── research.md          # Technology research and architecture (Phase 0/1)
├── data-model.md        # Detailed schema and entity definitions (Phase 1)
├── quickstart.md        # Setup and development instructions (Phase 1)
├── contracts/           # API request/response definitions (Phase 1)
└── tasks.md             # Implementation tasks (Phase 2 output)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI entry point
├── models.py            # SQLModel schemas
├── db.py                # Database engine and session
├── auth.py              # JWT verification dependency
├── schemas.py           # Pydantic validation models
├── config.py            # Pydantic Settings
├── routes/
│   └── tasks.py         # Task CRUD endpoints
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template

frontend/
├── app/                 # Next.js App Router flows
├── components/          # React components
│   ├── ui/              # Reusable atoms (Button, Input)
│   ├── auth/            # Auth forms (SignIn, SignUp)
│   ├── tasks/           # Task features (List, Card, Form)
│   └── layout/          # Wrappers (Header, Container)
├── lib/                 # Utilities (api.ts, auth.ts, types.ts)
├── public/              # Static assets
├── .env.example         # Environment template
├── package.json         # Node dependencies
└── tailwind.config.ts   # Styling config
```

**Structure Decision**: Web application structure with separate `frontend/` and `backend/` directories to maintain clean separation between services and allow independent deployment.

---

## Phase 0: Research & Architecture (research.md)

### Technology Research
- **Better Auth + FastAPI Integration**: Better Auth handles auth on frontend, issues JWT. Backend verifies JWT using shared `BETTER_AUTH_SECRET`.
- **SQLModel + Neon PG**: SQLModel provides type-safe ORM. Neon provides serverless PostgreSQL with easy branching.
- **Next.js 16 Auth Flow**: Using App Router with `use client` components for forms and `lib/auth.ts` for session management.

### Architectural Decisions
- **Shared Secret Auth**: Both frontend and backend share `BETTER_AUTH_SECRET` for JWT signing/verification.
- **RESTful Scoped Endpoints**: Endpoints take `user_id` in path (`/api/{user_id}/tasks`) for explicit scoping, verified against token payload.
- **Optimistic UI**: Use React state to update checkbox/delete status instantly while API request processes.

---

## Phase 1: Design & Contracts (data-model.md, quickstart.md, contracts/)

### Data Model (data-model.md)
- **User** (External): `id` (string), `email` (string), `name` (string), `password_hash` (string), `created_at` (datetime).
- **Task**: `id` (int, PK), `user_id` (string, FK), `title` (string, 1-200), `description` (string, 0-1000), `completed` (bool), `created_at` (datetime), `updated_at` (datetime).

### API Contracts (contracts/)
- **List**: `GET /api/{user_id}/tasks` -> `Task[]`
- **Create**: `POST /api/{user_id}/tasks` -> `Task`
- **Update**: `PUT /api/{user_id}/tasks/{id}` -> `Task`
- **Delete**: `DELETE /api/{user_id}/tasks/{id}` -> `204 No Content`
- **Toggle**: `PATCH /api/{user_id}/tasks/{id}/complete` -> `Task`

### Quickstart (quickstart.md)
1. Set up Neon DB and get connection string.
2. `cd backend && pip install -r requirements.txt && python main.py`
3. `cd frontend && npm install && npm run dev`
4. Register user and start creating tasks.

---

## Phase 2: Implementation Workflow (tasks.md)

*This section summarizes the high-level implementation order. Detailed tasks will be generated in tasks.md.*

### 1. Backend Foundation
- Project init, dependencies, and shell scripts.
- SQLModel models (User, Task).
- Database connector and session generator.
- Config management (Pydantic Settings).

### 2. Backend API
- JWT verification dependency (auth.py).
- Task CRUD routes (routes/tasks.py).
- Main app with CORS and startup logic.
- Integration test with curl.

### 3. Frontend Foundation
- Next.js init, Tailwind setup, component structure.
- Better Auth configuration (lib/auth.ts).
- TypeScript types and API client (lib/api.ts).
- Core UI components (Button, Input).

### 4. Authentication Features
- Signup form and page (/signup).
- Signin form and page (/).
- Auth context/session wrapper.
- Sign out functionality.

### 5. Task Management Features
- Dashboard layout and Header.
- TaskForm for creation.
- TaskList and TaskCard for display.
- Edit modal and Delete confirmation dialog.
- Status toggle with optimistic state.

### 6. Polish & Deployment
- Loading states (skeletons, spinners).
- Success/Error toast notifications.
- Responsive design audit.
- Final integration testing.

---

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| **JWT Sync Issues** | Ensure `BETTER_AUTH_SECRET` is identical in both .env files and minimum 32 characters. |
| **Database Connection** | Enable `pool_pre_ping=True` and connection pooling in SQLModel engine for Neon compatibility. |
| **Authentication Loops** | Implement clear redirection logic in frontend for 401 Unauthorized responses. |
| **CORS Denials** | Strictly configure `allow_origins` in FastAPI to include the frontend URL (local and production). |

---

## Success Validation

### Acceptance Tests
- **P1-Auth**: Register -> Sign Out -> Sign In -> Verify Dashboard access.
- **P2-CRUD**: Create task -> Verify in list -> Edit title -> Verify persist -> Toggle complete -> Verify strikethrough.
- **P3-Isolation**: Create Task as User A -> Sign Out -> Sign In as User B -> Verify User A's task is NOT visible.
- **P4-Stability**: Refresh page -> Verify tasks persist. Restart backend -> Verify tasks persist.

**Complexity Justification**: N/A (Plan follows constitution strictly)
