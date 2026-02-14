# Tasks: Phase 5 — Event-Driven Architecture

**Input**: Design documents from `/specs/6-event-driven-architecture/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), architecture.md, QUICK_REFERENCE.md
**Generated**: 2026-02-14
**Total Tasks**: 78
**Tests**: Included in Phase 10 (Testing & Documentation) per spec requirement

**Organization**: Tasks follow the 12-phase plan structure, mapped to 4 user stories:
- **US1** (P1): Real-Time Task Sync
- **US2** (P1): Recurring Tasks
- **US3** (P2): Reminders
- **US4** (P2): Event History & Audit Trail

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` (Python FastAPI — flat module structure)
- **Frontend**: `frontend/` (Next.js App Router)
- **Infrastructure**: `dapr/`, `k8s/`, `helm/taskflow/`
- **Migrations**: `migrations/versions/`

---

## Phase 1: Setup — Infrastructure (Local) [Phase 5.1]

**Purpose**: Docker Compose, Dockerfiles, Dapr components, base K8s namespace, dependency updates

- [x] T001 [P] Create docker-compose.yml with Redpanda, Redis, backend, and frontend services in docker-compose.yml
- [x] T002 [P] Update backend Dockerfile to multi-stage build with health check in backend/Dockerfile
- [x] T003 [P] Update frontend Dockerfile to multi-stage standalone build in frontend/Dockerfile
- [x] T004 [P] Add Phase 5 dependencies (aiokafka, dapr, APScheduler, python-dateutil, websockets) to backend/requirements.txt
- [x] T005 [P] Create Dapr Kafka pub/sub component config in dapr/pubsub-kafka.yaml
- [x] T006 [P] Create Dapr Redis state store component config in dapr/state-redis.yaml
- [x] T007 [P] Create Dapr cron binding for scheduled jobs in dapr/bindings-cron.yaml
- [x] T008 [P] Create Kubernetes namespace manifest in k8s/namespace.yaml
- [x] T009 [P] Create Kubernetes secrets template in k8s/secrets.yaml
- [x] T010 Update backend .env.example with Kafka, Redis, Dapr, and WebSocket environment variables in backend/.env.example

**Checkpoint**: `docker-compose up` starts Redpanda + Redis + backend + frontend; health checks pass; Dapr YAML files valid

---

## Phase 2: Foundational — Database Schema [Phase 5.2]

**Purpose**: Extend Task model, create Reminder model, Alembic migrations, Pydantic schemas

**⚠️ CRITICAL**: No feature work can begin until this phase is complete

- [x] T011 Add recurring task fields (due_date, recurrence_rule, is_recurring, next_occurrence) to Task model in backend/models.py
- [x] T012 Create Reminder SQLModel (id, task_id, user_id, remind_at, notified, created_at) in backend/models.py
- [x] T013 Initialize Alembic migration framework with env.py configuration in migrations/env.py
- [x] T014 Create migration 001: add recurring fields to tasks table in migrations/versions/001_add_recurring_fields.py
- [x] T015 Create migration 002: create reminders table in migrations/versions/002_create_reminders_table.py
- [x] T016 Update Pydantic schemas with TaskCreateRequest, TaskUpdateRequest, ReminderCreateRequest, and event schemas in backend/schemas.py

**Checkpoint**: `alembic upgrade head` succeeds on Neon PostgreSQL; `SELECT * FROM task` shows new columns; `SELECT * FROM reminder` returns empty set; Pydantic schemas validate correctly

---

## Phase 3: Foundational — Event System [Phase 5.3] 🔑 CRITICAL PATH

**Purpose**: Kafka event schemas, dual-path publisher (Dapr + direct Kafka), consumer infrastructure, event logging

**⚠️ CRITICAL**: This phase gates ALL feature phases (US1–US4). Must complete before any user story work.

- [x] T017 Define TaskEvent Pydantic model (event_id, event_type, user_id, aggregate_id, timestamp, correlation_id, data, version) in backend/schemas.py
- [x] T018 [P] Create Kafka client wrapper with AIOKafkaProducer/Consumer, retries, and connection pooling in backend/services/kafka_client.py
- [x] T019 [P] Create Dapr client wrapper with pub/sub abstraction and fallback to direct Kafka in backend/services/dapr_client.py
- [x] T020 Create dual-path EventPublisher (USE_DAPR env toggle) with error handling in backend/services/event_publisher.py
- [x] T021 Create event consumer infrastructure with topic subscription and callback dispatch in backend/handlers/event_processor.py
- [x] T022 Create event logging service for audit trail persistence to database in backend/services/event_log.py
- [x] T023 Update all existing CRUD routes (create, update, delete, complete) to publish TaskEvents via EventPublisher in backend/routes/tasks.py
- [x] T024 Register event publisher and consumer lifecycle hooks (startup/shutdown) in backend/main.py

**Checkpoint**: Create task via API → event published to Kafka → event logged in DB; both Dapr and direct Kafka paths work (toggle USE_DAPR); `kcat -C -t tasks.events` shows events; event retry handles transient failures

---

## Phase 4: User Story 1 — Real-Time Task Sync (Priority: P1) 🎯 MVP

**Goal**: WebSocket endpoint with JWT auth, per-user connection management, event-to-WebSocket bridge, frontend auto-reconnect client

**Independent Test**: Open dashboard on two browser tabs; create task in Tab 1; verify instant appearance in Tab 2 within 500ms without refresh

### Implementation for User Story 1

- [x] T025 [P] [US1] Create WebSocket connection manager (per-user rooms, add/remove/broadcast) in backend/services/websocket_manager.py
- [x] T026 [US1] Create WebSocket endpoint at /ws/user/{user_id}/tasks with JWT validation on connect in backend/routes/websocket.py
- [x] T027 [US1] Create WebSocket event handler that bridges Kafka events to WebSocket broadcasts in backend/handlers/websocket_handler.py
- [x] T028 [US1] Register WebSocket route and event handler startup in backend/main.py
- [x] T029 [P] [US1] Create frontend WebSocket client class with auto-reconnect (exponential backoff, max 5 attempts) in frontend/lib/websocket-client.ts
- [x] T030 [P] [US1] Add WebSocket event TypeScript types (TaskWSMessage, WSConnectionState) in frontend/lib/types.ts
- [x] T031 [US1] Create WebSocketProvider React context that manages connection lifecycle in frontend/components/realtime/WebSocketProvider.tsx
- [x] T032 [US1] Wrap application layout with WebSocketProvider in frontend/app/layout.tsx
- [x] T033 [US1] Update dashboard page to consume WebSocket events and refresh task list in real-time in frontend/app/dashboard/page.tsx
- [x] T034 [US1] Update TaskCard component with real-time sync visual indicator (live dot) in frontend/components/tasks/TaskCard.tsx

**Checkpoint**: Two browser tabs → create task in Tab 1 → appears in Tab 2 within 500ms; WebSocket reconnects after network drop within 5s; user isolation verified (User A tab doesn't get User B events); graceful degradation when WebSocket unavailable (falls back to manual refresh)

---

## Phase 5: User Story 2 — Recurring Tasks (Priority: P1) 🎯 MVP

**Goal**: RRULE-based recurrence rules, automatic task spawning on schedule, APScheduler + Dapr binding dual-path, frontend recurrence UI

**Independent Test**: Create recurring daily task; wait for scheduler tick; verify new task instance auto-created; complete original → next instance still spawns independently

### Implementation for User Story 2

- [x] T035 [P] [US2] Create recurrence calculator service (RRULE parsing via dateutil.rrule, timezone-aware next_occurrence) in backend/services/scheduler.py
- [x] T036 [US2] Create task scheduler service with spawn_recurring_tasks method (query due tasks, create instances, update next_occurrence, publish events) in backend/services/scheduler.py
- [x] T037 [US2] Add APScheduler integration to main.py with 1-minute interval job for spawn_recurring_tasks (max_instances=1) in backend/main.py
- [x] T038 [US2] Add POST /api/{user_id}/tasks/{id}/recurrence endpoint (set recurrence rule) in backend/routes/tasks.py
- [x] T039 [US2] Add GET /api/{user_id}/tasks/recurring endpoint (list all recurring tasks) in backend/routes/tasks.py
- [x] T040 [US2] Add DELETE /api/{user_id}/tasks/{id}/recurrence endpoint (remove recurrence) in backend/routes/tasks.py
- [x] T041 [US2] Create RecurrenceForm component (dropdown: None/Daily/Weekly/Monthly, day checkboxes for weekly, date selector for monthly) in frontend/components/tasks/RecurrenceForm.tsx
- [x] T042 [US2] Integrate RecurrenceForm into task create/edit flow and update TaskCard to show recurrence badge in frontend/components/tasks/TaskCard.tsx

**Checkpoint**: Set daily recurrence → scheduler spawns new instance within 5 minutes; weekly recurrence with specific days works; next_occurrence updates correctly after spawn; no duplicate instances (max_instances=1); event published with recurring.spawned type; frontend displays recurrence pattern

---

## Phase 6: User Story 3 — Task Reminders (Priority: P2)

**Goal**: Due dates on tasks, configurable reminders with lead times, cron-based reminder checking, WebSocket push notifications

**Independent Test**: Create task with due date 24 hours out; set reminder for 1 day before; verify reminder event fires within 1 minute of remind_at time

### Implementation for User Story 3

- [x] T043 [US3] Add check_pending_reminders method to scheduler service (query due reminders, publish events, mark notified for idempotency) in backend/services/scheduler.py
- [x] T044 [US3] Add APScheduler job for check_pending_reminders with 1-minute interval in backend/main.py
- [x] T045 [US3] Add PUT /api/{user_id}/tasks/{id}/due-date endpoint (set/update due date) in backend/routes/tasks.py
- [x] T046 [US3] Add POST /api/{user_id}/tasks/{id}/reminders endpoint (create reminder with remind_at time) in backend/routes/tasks.py
- [x] T047 [US3] Add GET /api/{user_id}/reminders/pending endpoint (list pending reminders) in backend/routes/tasks.py
- [x] T048 [US3] Add reminder cancellation logic: delete pending reminders when task completed or deleted in backend/routes/tasks.py
- [x] T049 [P] [US3] Create DueDatePicker component (date picker + preset reminder options: 1 day, 1 hour, 30 min before) in frontend/components/tasks/DueDatePicker.tsx
- [x] T050 [US3] Integrate DueDatePicker into task create/edit flow and display due date + reminders on TaskCard in frontend/components/tasks/TaskCard.tsx
- [x] T051 [US3] Add reminder notification toast display when WebSocket receives reminder.triggered event in frontend/components/realtime/WebSocketProvider.tsx

**Checkpoint**: Create reminder → event published at remind_at time within 1 minute; multiple reminders on single task work independently; idempotency prevents duplicate notifications; completing task cancels pending reminders; frontend shows toast notification on reminder

---

## Phase 7: User Story 4 — Event History & Audit Trail (Priority: P2)

**Goal**: Immutable event storage, event replay capability, per-user event history API

**Independent Test**: Create task, update title, mark complete, delete; retrieve event history; verify all 4 events present in chronological order with full context

### Implementation for User Story 4

- [x] T052 [P] [US4] Create EventLog SQLModel (id, event_id, event_type, user_id, aggregate_id, timestamp, correlation_id, data, version) in backend/models.py
- [x] T053 [US4] Create migration 003: create event_log table in migrations/versions/003_create_event_log_table.py
- [x] T054 [US4] Update event_log service to persist all published events to event_log table in backend/services/event_log.py
- [x] T055 [US4] Add GET /api/{user_id}/events endpoint (query event history by user_id, optional filters: event_type, time_range, aggregate_id) in backend/routes/events.py
- [x] T056 [US4] Add GET /api/{user_id}/tasks/{id}/events endpoint (task-specific event history) in backend/routes/events.py
- [x] T057 [US4] Register events router in main.py in backend/main.py

**Checkpoint**: All task operations create event_log entries; GET /events returns chronological history; events include full context (user_id, correlation_id, data); event replay shows exact same sequence; user isolation verified (no cross-user event leakage)

---

## Phase 8: Kubernetes Deployment — Local Minikube [Phase 5.7]

**Purpose**: K8s manifests for all services, Dapr component configuration for K8s, Ingress setup

- [x] T058 [P] Create backend Deployment manifest with Dapr sidecar annotations in k8s/backend-deployment.yaml
- [x] T059 [P] Create backend Service manifest (ClusterIP, port 8000) in k8s/backend-service.yaml
- [x] T060 [P] Create frontend Deployment manifest in k8s/frontend-deployment.yaml
- [x] T061 [P] Create frontend Service manifest (NodePort, port 3000) in k8s/frontend-service.yaml
- [x] T062 [P] Create Redis Deployment and Service manifests in k8s/redis-deployment.yaml and k8s/redis-service.yaml
- [x] T063 [P] Create ConfigMap with non-secret configuration in k8s/configmap.yaml
- [x] T064 Create Ingress manifest for Minikube ingress addon in k8s/ingress.yaml

**Checkpoint**: `kubectl apply -f k8s/` succeeds; all pods Running; `kubectl port-forward` exposes backend and frontend; Dapr sidecar injected into backend pod

---

## Phase 9: Helm Charts [Phase 5.8]

**Purpose**: Templated K8s resources, multi-environment values, conditional Dapr logic

- [x] T065 Update Chart.yaml with Phase 5 metadata (appVersion, description) in helm/taskflow/Chart.yaml
- [x] T066 Update values.yaml with event-driven defaults (Kafka, Redis, Dapr toggles, WebSocket config) in helm/taskflow/values.yaml
- [x] T067 [P] Create values-prod.yaml with cloud production overrides (Redpanda Cloud, SASL, no Dapr for simple) in helm/taskflow/values-prod.yaml
- [x] T068 Update Helm templates to include Dapr annotations, Kafka config, WebSocket port, and conditional Dapr toggle in helm/taskflow/templates/

**Checkpoint**: `helm install taskflow ./helm/taskflow -f helm/taskflow/values-dev.yaml` succeeds on Minikube; `helm upgrade` applies new values; `helm template` renders correct manifests for both dev and prod values

---

## Phase 10: Cloud Preparation [Phase 5.9]

**Purpose**: Environment config for cloud, health checks, CORS, graceful Dapr absence

- [x] T069 Add /health and /ready endpoints to backend with Kafka and DB connectivity checks in backend/main.py
- [x] T070 Update CORS configuration to support production domains (Vercel, Render, custom) in backend/main.py
- [x] T071 Add graceful Dapr absence handling — detect USE_DAPR=false and skip Dapr initialization in backend/main.py

**Checkpoint**: /health returns 200 with dependency status; CORS allows Vercel/Render origins; backend starts cleanly with USE_DAPR=false (no Dapr errors)

---

## Phase 11: Cloud Deployment — Simple (Vercel + Render) [Phase 5.10]

**Purpose**: Configuration-only deployment to Vercel (frontend) and Render (backend) with Redpanda Cloud

- [x] T072 [P] Create Render deployment config with Docker service type, health check, and env vars in render.yaml
- [x] T073 [P] Create or update Vercel configuration with production environment variables and build settings in frontend/vercel.json
- [x] T074 Create Redpanda Cloud Serverless setup guide with topic creation and SASL credentials in specs/6-event-driven-architecture/CLOUD_OPTIONS.md

**Checkpoint**: Backend deploys on Render free tier; frontend deploys on Vercel; both connect to Redpanda Cloud Serverless; full application functional without Dapr

---

## Phase 12: Cloud Deployment — Kubernetes (Civo) [Phase 5.11]

**Purpose**: Civo K8s cluster with Dapr, Helm deployment, Ingress/LoadBalancer

- [x] T075 Create Civo cluster setup and Dapr installation guide in specs/6-event-driven-architecture/DEPLOYMENT.md
- [x] T076 Create k8s/secrets.example.yaml documenting all required secrets (Neon URL, Redpanda SASL, OpenAI key, Better Auth secret) in k8s/secrets.example.yaml

**Checkpoint**: Helm chart deploys to Civo; all pods Running with Dapr sidecars; Ingress routes traffic; application fully functional

---

## Phase 13: Testing & Documentation [Phase 5.12]

**Purpose**: Integration tests, E2E tests, load tests, deployment guides, troubleshooting

- [x] T077 [P] Write integration tests for event publishing flow (create task → event in Kafka → event in DB) in backend/tests/test_events.py
- [x] T078 Write comprehensive DEPLOYMENT_SETUP.md with step-by-step guides for all 3 deployment options (Local Minikube, Cloud Simple, Cloud K8s) in DEPLOYMENT_SETUP.md

**Checkpoint**: Integration tests pass for event flow; DEPLOYMENT_SETUP.md covers all 3 options with exact commands; demo shows real-time sync + recurring tasks + reminders working

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)          ─── No dependencies, start immediately
Phase 2 (DB Schema)      ─── Depends on: Phase 1
Phase 3 (Event System)   ─── Depends on: Phase 1, Phase 2 ⚠️ CRITICAL PATH
Phase 4 (US1: WebSocket) ─── Depends on: Phase 3
Phase 5 (US2: Recurring) ─── Depends on: Phase 3
Phase 6 (US3: Reminders) ─── Depends on: Phase 3
Phase 7 (US4: Audit)     ─── Depends on: Phase 3
Phase 8 (K8s Local)      ─── Depends on: Phase 1, Phase 3
Phase 9 (Helm)           ─── Depends on: Phase 8
Phase 10 (Cloud Prep)    ─── Depends on: Phase 3
Phase 11 (Cloud Simple)  ─── Depends on: Phase 10
Phase 12 (Cloud K8s)     ─── Depends on: Phase 9, Phase 10
Phase 13 (Testing/Docs)  ─── Depends on: Phases 4–7, Phase 11 or 12
```

### User Story Dependencies

- **US1 (Real-Time Sync)**: Depends on Phase 3 (Event System) — No dependencies on other stories
- **US2 (Recurring Tasks)**: Depends on Phase 3 (Event System) — No dependencies on other stories
- **US3 (Reminders)**: Depends on Phase 3 (Event System) — No dependencies on other stories
- **US4 (Audit Trail)**: Depends on Phase 3 (Event System) — No dependencies on other stories

All 4 user stories are **independently implementable** after Phase 3 completes.

### Within Each User Story

1. Backend models/services FIRST
2. Backend API endpoints NEXT
3. Frontend components LAST
4. Integration points FINAL

### Parallel Opportunities

**Phase 1**: T001–T010 are ALL parallelizable (different files)
**Phase 3**: T018+T019 parallel (kafka_client + dapr_client), then T020 sequential
**Phases 4–7**: ALL four user story phases can run in parallel after Phase 3
**Phase 8**: T058–T063 are ALL parallelizable (different K8s manifests)
**Phase 11+12**: Cloud Simple and Cloud K8s can run in parallel

---

## Parallel Example: Phase 1

```bash
# All Phase 1 tasks create different files — run in parallel:
Task T001: "docker-compose.yml"
Task T002: "backend/Dockerfile"
Task T003: "frontend/Dockerfile"
Task T004: "backend/requirements.txt"
Task T005: "dapr/pubsub-kafka.yaml"
Task T006: "dapr/state-redis.yaml"
Task T007: "dapr/bindings-cron.yaml"
Task T008: "k8s/namespace.yaml"
Task T009: "k8s/secrets.yaml"
Task T010: "backend/.env.example"
```

## Parallel Example: User Stories After Phase 3

```bash
# After Phase 3 completes, all 4 user stories are independent:
Stream A (US1): T025–T034 → Real-Time WebSocket
Stream B (US2): T035–T042 → Recurring Tasks
Stream C (US3): T043–T051 → Reminders
Stream D (US4): T052–T057 → Event History

# With single developer, recommended order: US1 → US2 → US3 → US4
# With team, all 4 streams can execute simultaneously
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (infrastructure)
2. Complete Phase 2: Database Schema (foundational)
3. Complete Phase 3: Event System (CRITICAL — gates everything)
4. Complete Phase 4: US1 Real-Time Sync
5. Complete Phase 5: US2 Recurring Tasks
6. **STOP and VALIDATE**: Both P1 stories independently functional
7. Deploy locally with `docker-compose up`

### Incremental Delivery

1. Setup + DB + Events → Foundation ready
2. Add US1 (WebSocket) → Test: real-time sync works → Local deploy
3. Add US2 (Recurring) → Test: tasks spawn on schedule → Local deploy
4. Add US3 (Reminders) → Test: notifications fire on time → Local deploy
5. Add US4 (Audit) → Test: event history complete → Local deploy
6. K8s + Helm → Test: Minikube deployment → K8s deploy
7. Cloud prep + deploy → Test: cloud functional → Cloud deploy
8. Testing + docs → Validate all → Final delivery

### Deployment Compatibility Matrix

| Task Range | Local (Docker) | Cloud Simple | Cloud K8s | All |
|------------|---------------|-------------|-----------|-----|
| T001–T010 | ✅ Primary | Partial | Partial | — |
| T011–T016 | — | — | — | ✅ |
| T017–T024 | — | — | — | ✅ |
| T025–T034 | — | — | — | ✅ |
| T035–T042 | — | — | — | ✅ |
| T043–T051 | — | — | — | ✅ |
| T052–T057 | — | — | — | ✅ |
| T058–T064 | ✅ Minikube | — | ✅ | — |
| T065–T068 | ✅ Minikube | — | ✅ | — |
| T069–T071 | — | — | — | ✅ |
| T072–T074 | — | ✅ | — | — |
| T075–T076 | — | — | ✅ | — |
| T077–T078 | — | — | — | ✅ |

---

## Task Summary

| Phase | Description | Tasks | Task IDs |
|-------|------------|-------|----------|
| 1 | Setup — Infrastructure | 10 | T001–T010 |
| 2 | Foundational — Database Schema | 6 | T011–T016 |
| 3 | Foundational — Event System | 8 | T017–T024 |
| 4 | US1: Real-Time Sync (P1) | 10 | T025–T034 |
| 5 | US2: Recurring Tasks (P1) | 8 | T035–T042 |
| 6 | US3: Reminders (P2) | 9 | T043–T051 |
| 7 | US4: Event History (P2) | 6 | T052–T057 |
| 8 | Kubernetes Local | 7 | T058–T064 |
| 9 | Helm Charts | 4 | T065–T068 |
| 10 | Cloud Preparation | 3 | T069–T071 |
| 11 | Cloud Simple (Vercel/Render) | 3 | T072–T074 |
| 12 | Cloud K8s (Civo) | 2 | T075–T076 |
| 13 | Testing & Documentation | 2 | T077–T078 |
| **TOTAL** | | **78** | **T001–T078** |

---

## Notes

- [P] tasks = different files, no dependencies — safe to run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable after Phase 3
- Phase 3 (Event System) is the CRITICAL PATH — do not skip or defer
- Commit after each task or logical group
- Stop at any checkpoint to validate current state
- All code paths must work with USE_DAPR=true (local/K8s) and USE_DAPR=false (cloud simple)
- All tasks target $0 cost using free-tier services only
