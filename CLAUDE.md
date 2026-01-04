# CLAUDE.md - TaskFlow Phase 2 Implementation Notes

## Project Overview
TaskFlow Web is a multi-user todo application that evolved from a Phase 1 console app. It adheres to **Spec-Driven Development (SDD)** principles.

## Spec Architecture
- `specs/sp.constitution`: Project principles & security standards
- `specs/sp.specify`: Functional requirements & user journeys
- `specs/sp.plan`: Technical implementation strategy
- `specs/sp.tasks`: Itemized task breakdown (T-201 to T-237)

## Implementation State
✓ **Phase A (Backend Base)**: Completed. FastAPI, SQLModel, JWT middleware, CRUD routes.
✓ **Phase B (Frontend Base)**: Completed. Next.js, Better Auth config, API client, Atomic UI.
✓ **Phase C (Task Management)**: Completed. Dashboard, CRUD forms, Modals, State management.
✓ **Phase D (Polish & Documentation)**: Completed. README, system notes.

## Key Technical Decisions
1. **Shared Secret Auth**: Both services share `BETTER_AUTH_SECRET` for HS256 JWT signature verification.
2. **User Isolation**: Middleware extracts `user_id` from JWT and enforces match with path parameters.
3. **Pydantic + SQLModel**: Unified data validation from database layer to API boundary.
4. **Tailwind + Lucide**: Clean, accessible component design with mobile-first approach.

## Command Reference
- **Backend Run**: `uvicorn backend.main:app --reload`
- **Frontend Run**: `npm run dev --prefix frontend`
- **Manual API Test**: See `backend/README.md` for curl examples.

## Task Status: DONE
- [X] T-201 to T-215 (Backend Foundation & API)
- [X] T-216 to T-224 (Frontend Foundation & Auth UI)
- [X] T-225 to T-230 (Dashboard & CRUD UI)
- [X] T-231 to T-237 (Polish & Publishing)
