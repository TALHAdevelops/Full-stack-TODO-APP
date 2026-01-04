# Task Breakdown: TaskFlow Web Application (Phase 2)

This document breaks down the implementation of TaskFlow Web into atomic, sequential tasks.

**Branch**: `2-taskflow-web-app` | **Date**: 2025-12-31 | **Plan**: [specs/2-taskflow-web-app/plan.md](specs/2-taskflow-web-app/plan.md)

## Status Summary

- **Total Tasks**: 37
- **Completed**: 0
- **In Progress**: 0
- **Remaining**: 37

---

## Phase A: Backend Foundation (T-201 to T-215)

| ID | Task Title | Status | Dependency |
|----|------------|--------|------------|
| T-201 | Set up Neon PostgreSQL database | [ ] | None |
| T-202 | Initialize FastAPI backend project | [ ] | T-201 |
| T-203 | Create SQLModel database models | [ ] | T-202 |
| T-204 | Implement database connection & init | [ ] | T-203 |
| T-205 | Create Pydantic validation schemas | [ ] | T-204 |
| T-206 | Implement JWT verification middleware | [ ] | T-205 |
| T-207 | Implement configuration management | [ ] | T-206 |
| T-208 | Implement GET /api/{user_id}/tasks | [ ] | T-207 |
| T-209 | Implement POST /api/{user_id}/tasks | [ ] | T-208 |
| T-210 | Implement GET /api/{user_id}/tasks/{id} | [ ] | T-209 |
| T-211 | Implement PUT /api/{user_id}/tasks/{id} | [ ] | T-210 |
| T-212 | Implement DELETE /api/{user_id}/tasks/{id} | [ ] | T-211 |
| T-213 | Implement PATCH /api/{user_id}/tasks/{id}/complete | [ ] | T-212 |
| T-214 | Configure CORS and complete main.py | [ ] | T-213 |
| T-215 | Test backend API with curl/Postman | [ ] | T-214 |

---

## Phase B: Frontend Foundation (T-216 to T-224)

| ID | Task Title | Status | Dependency |
|----|------------|--------|------------|
| T-216 | Initialize Next.js frontend project | [ ] | T-215 |
| T-217 | Install and configure Better Auth | [ ] | T-216 |
| T-218 | Create TypeScript types and interfaces | [ ] | T-217 |
| T-219 | Create API client functions | [ ] | T-218 |
| T-220 | Create reusable UI (Button, Input) | [ ] | T-219 |
| T-221 | Create SignUpForm component | [ ] | T-220 |
| T-222 | Create SignInForm component | [ ] | T-221 |
| T-223 | Create landing/sign-in page (/) | [ ] | T-222 |
| T-224 | Create sign-up page (/signup) | [ ] | T-223 |

---

## Phase C: Task Management UI (T-225 to T-230)

| ID | Task Title | Status | Dependency |
|----|------------|--------|------------|
| T-225 | Create dashboard Header component | [ ] | T-224 |
| T-226 | Create TaskCard component | [ ] | T-225 |
| T-227 | Create TaskForm component | [ ] | T-226 |
| T-228 | Create TaskList component | [ ] | T-227 |
| T-229 | Create Dashboard page with CRUD | [ ] | T-228 |
| T-230 | Implement delete confirmation dialog | [ ] | T-229 |

---

## Phase D: Polish & Deployment (T-231 to T-237)

| ID | Task Title | Status | Dependency |
|----|------------|--------|------------|
| T-231 | Add error handling & loading states | [ ] | T-230 |
| T-232 | Responsive design audit (all screens) | [ ] | T-231 |
| T-233 | Full end-to-end integration testing | [ ] | T-232 |
| T-234 | Deploy frontend to Vercel | [ ] | T-233 |
| T-235 | Write comprehensive README.md | [ ] | T-234 |
| T-236 | Update CLAUDE.md with system notes | [ ] | T-235 |
| T-237 | Create demo video (under 90 sec) | [ ] | T-236 |

---

## Detailed Task Definitions

### Phase A: Backend Foundation

**T-201: Set up Neon PostgreSQL database**
- **Description**: Create Neon account and database project for cloud storage.
- **Criteria**: Obtain connection string; Create `.env` and `.env.example` in `backend/`.
- **References**: [spec.md: FR-8], [plan.md: DB Connection]

**T-202: Initialize FastAPI backend project**
- **Description**: Set up folder structure and dependencies.
- **Criteria**: Create `backend/requirements.txt`, `main.py` with health check, and `.gitignore`.
- **References**: [plan.md: Backend Part 2]

**T-203: Create SQLModel database models**
- **Description**: Implement User and Task schemas for the database.
- **Criteria**: `models.py` with `User` and `Task` class definitions, relationships, and constraints.
- **References**: [spec.md: Data Requirements], [plan.md: Backend Part 1]

**T-204: Implement database connection & init**
- **Description**: Logic for engine creation and session injection.
- **Criteria**: `db.py` with `get_session` generator and `create_db_and_tables` startup logic.
- **References**: [plan.md: Backend Part 2]

**T-205: Create Pydantic validation schemas**
- **Description**: Define request and response shapes.
- **Criteria**: `schemas.py` with `TaskCreate`, `TaskUpdate`, and `TaskResponse` models.
- **References**: [spec.md: FR-7], [plan.md: Backend Part 4]

**T-206: Implement JWT verification middleware**
- **Description**: Middleware to extract and verify `user_id` from Bearer tokens.
- **Criteria**: `auth.py` using `PyJWT` decoding with shared secret; Returns `user_id` or 401.
- **References**: [spec.md: FR-1, FR-12], [plan.md: Backend Part 3]

**T-207: Implement configuration management**
- **Description**: Type-safe settings using Pydantic Settings.
- **Criteria**: `config.py` reading from `.env`; Exports `settings` singleton.
- **References**: [plan.md: Backend Part 6]

**T-208: Implement GET /api/{user_id}/tasks**
- **Description**: Fetch all tasks for the identified user.
- **Criteria**: Route handler that verifies path `user_id` matches token; returns list sorted by date.
- **References**: [spec.md: FR-3], [plan.md: Backend Part 5]

**T-209: Implement POST /api/{user_id}/tasks**
- **Description**: Create a new task.
- **Criteria**: Validates input; sets `user_id` from token; returns 201 with created task.
- **References**: [spec.md: FR-2], [plan.md: Backend Part 5]

**T-210: Implement GET /api/{user_id}/tasks/{id}**
- **Description**: Fetch single task details.
- **Criteria**: Returns 404 if not found or if user doesn't own the task.
- **References**: [spec.md: FR-3], [plan.md: Backend Part 5]

**T-211: Implement PUT /api/{user_id}/tasks/{id}**
- **Description**: Update task title/description.
- **Criteria**: Partial update support; auto-updates `updated_at` timestamp.
- **References**: [spec.md: FR-4], [plan.md: Backend Part 5]

**T-212: Implement DELETE /api/{user_id}/tasks/{id}**
- **Description**: Remove task.
- **Criteria**: Returns 204 No Content; verifies ownership before deletion.
- **References**: [spec.md: FR-5], [plan.md: Backend Part 5]

**T-213: Implement PATCH /api/{user_id}/tasks/{id}/complete**
- **Description**: Toggle status.
- **Criteria**: Logic to flip `completed` boolean; returns updated task object.
- **References**: [spec.md: FR-6], [plan.md: Backend Part 5]

**T-214: Configure CORS and complete main.py**
- **Description**: Final app wiring.
- **Criteria**: Add `CORSMiddleware` with frontend origin; include all routers; health endpoint.
- **References**: [plan.md: Backend Part 7]

**T-215: Test backend API with curl/Postman**
- **Description**: Manual verification of API isolation and logic.
- **Criteria**: Successfully run all 5 CRUD operations with a manual test token.
- **References**: [plan.md: Testing Strategy]

### Phase B: Frontend Foundation

**T-216: Initialize Next.js frontend project**
- **Description**: Framework setup.
- **Criteria**: Next.js 16+ App Router, TypeScript, Tailwind CSS configuration.
- **References**: [plan.md: Frontend Project Structure]

**T-217: Install and configure Better Auth**
- **Description**: Setup of authentication client.
- **Criteria**: `lib/auth.ts` config; `api/auth/[...all]` route; `.env.local` with secrets.
- **References**: [plan.md: Frontend Part 2]

**T-218: Create TypeScript types and interfaces**
- **Description**: Data contract definitions.
- **Criteria**: `lib/types.ts` containing `User`, `Task`, `ApiError` interfaces.
- **References**: [plan.md: Frontend Part 1]

**T-219: Create API client functions**
- **Description**: Fetch wrappers with JWT injection.
- **Criteria**: `lib/api.ts` with typed methods for all 5 CRUD operations; Handles 401 redirects.
- **References**: [plan.md: Frontend Part 3]

**T-220: Create reusable UI (Button, Input)**
- **Description**: Atoms for the UI system.
- **Criteria**: Typed props, Tailwind styling, loading states, error boundaries.
- **References**: [plan.md: Frontend Part 4]

**T-221: Create SignUpForm component**
- **Description**: Auth registration UI.
- **Criteria**: Validation for email/password; loading state; redirect on success.
- **References**: [spec.md: Journey 1]

**T-222: Create SignInForm component**
- **Description**: Auth login UI.
- **Criteria**: Error handling for invalid credentials; redirect on success.
- **References**: [spec.md: Journey 2]

**T-223: Create landing/sign-in page (/)**
- **Description**: Public entry point.
- **Criteria**: Clean landing UI; SignIn form integration.
- **References**: [spec.md: Journey 2]

**T-224: Create sign-up page (/signup)**
- **Description**: Registration entry point.
- **Criteria**: Clean signup UI; SignUp form integration.
- **References**: [spec.md: Journey 1]

### Phase C: Task Management UI

**T-225: Create dashboard Header component**
- **Description**: Top navigation with user identity.
- **Criteria**: Email display; Sign Out button implementation.
- **References**: [plan.md: Frontend Part 5]

**T-226: Create TaskCard component**
- **Description**: Task item display.
- **Criteria**: Checkbox for toggle; strikethrough for completed; edit/delete buttons.
- **References**: [spec.md: Journey 4, 7]

**T-227: Create TaskForm component**
- **Description**: Creation and edit implementation.
- **Criteria**: Shared form for adding/updating; validation counters (200/1000).
- **References**: [spec.md: Journey 3, 5]

**T-228: Create TaskList component**
- **Description**: Collection manager.
- **Criteria**: Handles loading skeletons and empty states.
- **References**: [spec.md: Journey 4]

**T-229: Create Dashboard page with CRUD**
- **Description**: Protected management center.
- **Criteria**: Auth guard; State orchestration for all 5 CRUD operations.
- **References**: [spec.md: Journeys 1-8]

**T-230: Implement delete confirmation dialog**
- **Description**: Safety modal.
- **Criteria**: Confirmation step before permanent deletion.
- **References**: [spec.md: Journey 6]

### Phase D: Polish & Deployment

**T-231: Add error handling & loading states**
- **Description**: User feedback optimization.
- **Criteria**: Success/Error toasts; button spinners; skeleton screens.
- **References**: [spec.md: Error Handling Requirements]

**T-232: Responsive design audit (all screens)**
- **Description**: Visual consistency across viewports.
- **Criteria**: Verification of mobile (320px+), tablet, and desktop layouts.
- **References**: [spec.md: AC-UX-7 to 9]

**T-233: Full end-to-end integration testing**
- **Description**: Path verification.
- **Criteria**: Manual signup -> create -> edit -> toggle -> delete flows work perfectly.
- **References**: [spec.md: Acceptance Criteria Summary]

**T-234: Deploy frontend to Vercel**
- **Description**: Production deployment.
- **Criteria**: Successful public URL; all environment variables configured; CORS works.
- **References**: [plan.md: Deployment Architecture]

**T-235: Write comprehensive README.md**
- **Description**: Project documentation.
- **Criteria**: Setup steps; architecture overview; tech stack.
- **References**: [plan.md: Backend README]

**T-236: Update CLAUDE.md with system notes**
- **Description**: AI development documentation.
- **Criteria**: Accurate tech notes; running commands; common tasks.
- **References**: [plan.md: Implementation Order]

**T-237: Create demo video (under 90 sec)**
- **Description**: Submission preparation.
- **Criteria**: Shows all core CRUD + auth features in < 90 seconds.
- **References**: [spec.md: Success Criteria]
