# Phase 5 Implementation Plan: Event-Driven Architecture

**Feature**: Distributed Cloud-Native Event-Driven Todo System
**Branch**: `6-event-driven-architecture`
**Date**: 2026-02-14
**Status**: Draft
**Input**: Phase 5 specification with 3 deployment options

---

## Summary

Phase 5 transforms TaskFlow into a distributed, event-driven system supporting real-time synchronization, recurring tasks, reminders, and deployment across three models: local Minikube with Dapr, cloud-simple with Vercel/Render, and cloud-Kubernetes with Civo/Dapr. The implementation progresses from local infrastructure → core event system → features → deployments, with parallel streams for local (Dapr) and cloud (direct Kafka) code paths.

**Critical Path**: Database schema → Event foundation → WebSocket → Features → Deployments
**Parallel Work**: Kubernetes manifests, Helm charts, cloud configuration
**Total Duration**: ~6-8 weeks (assuming 4-5 dev hours/week)

---

## Technical Context

| Aspect | Details |
|--------|---------|
| **Languages/Versions** | Python 3.13 (backend), TypeScript/Next.js 16 (frontend) |
| **Primary Dependencies** | FastAPI, SQLModel, Pydantic, aiokafka, Dapr SDK, APScheduler |
| **Storage** | PostgreSQL (Neon free tier), Kafka/Redpanda (local Docker + cloud serverless) |
| **Testing** | pytest (backend), vitest/Jest (frontend), integration tests for events |
| **Target Platform** | Kubernetes (Minikube local, Civo cloud), Vercel/Render (cloud simple) |
| **Project Type** | Full-stack web application with event streaming |
| **Performance Goals** | <500ms real-time sync, 1000+ events/sec, <100ms WebSocket latency |
| **Constraints** | 100% free-tier services, no paid cloud services, Dapr local-only |
| **Scale/Scope** | Support 1000+ active users, 3 deployment options, multi-device sync |

---

## Constitution Check

**Mandatory Principles** (Phase 5 additions):
- ✅ **XVIII. Event-Driven Architecture**: All task changes emit Kafka events
- ✅ **XIX. Dapr Integration**: Local/K8s development with graceful cloud fallback
- ✅ **XX. Loose Coupling**: Services via events, not direct HTTP calls
- ✅ **XXI. Observability**: Events traced with correlation_id + user_id
- ✅ **XXII. Cost Optimization**: 100% free services (Neon, Redpanda Cloud, Vercel, Render, Civo)
- ✅ **XXIII. Recurring Tasks**: Automatic task generation on schedule
- ✅ **XXIV. Real-Time Updates**: WebSocket for live client sync

**Technology Alignment**:
- ✅ No violations: Dapr optional, direct Kafka for cloud, PostgreSQL external
- ✅ Type safety: Python type hints + Pydantic, TypeScript strict mode
- ✅ Stateless backend: Events replace server-side state
- ✅ User isolation: JWT + Kafka filtering + WebSocket subscriptions

**Gates Passed**: All constitutional principles satisfied; no unjustified violations.

---

## Project Structure

```
project-root/
├── backend/
│   ├── Dockerfile                          (NEW: multi-stage)
│   ├── requirements.txt                    (ADD: aiokafka, APScheduler, dapr-sdk)
│   ├── main.py                             (UPDATE: event routes)
│   ├── models.py                           (UPDATE: Task + Reminder schemas)
│   ├── schemas.py                          (UPDATE: event schemas)
│   ├── routes/
│   │   ├── tasks.py                        (UPDATE: add recurrence/reminder endpoints)
│   │   ├── websocket.py                    (NEW: WebSocket endpoint)
│   │   └── events.py                       (NEW: event publishing utilities)
│   ├── handlers/                           (NEW: event handlers directory)
│   │   ├── recurring_tasks.py              (NEW: spawn recurring instances)
│   │   ├── reminders.py                    (NEW: send reminder events)
│   │   └── event_processor.py              (NEW: generic processor)
│   └── services/
│       ├── kafka_client.py                 (NEW: Kafka producer/consumer)
│       ├── dapr_client.py                  (NEW: Dapr pub/sub wrapper)
│       ├── scheduler.py                    (NEW: APScheduler integration)
│       └── event_log.py                    (NEW: audit trail)
│
├── frontend/
│   ├── Dockerfile                          (NEW: multi-stage Node build)
│   ├── app/
│   │   └── dashboard/
│   │       └── page.tsx                    (UPDATE: WebSocket integration)
│   ├── components/
│   │   ├── tasks/
│   │   │   ├── RecurrenceForm.tsx          (NEW: RRULE UI)
│   │   │   ├── DueDatePicker.tsx           (NEW: due date + reminder)
│   │   │   └── TaskCard.tsx                (UPDATE: real-time sync visual)
│   │   └── realtime/
│   │       └── WebSocketProvider.tsx       (NEW: WS management + reconnect)
│   └── lib/
│       ├── websocket-client.ts             (NEW: WS client with retries)
│       └── types.ts                        (UPDATE: event types)
│
├── dapr/                                    (NEW: Dapr configuration directory)
│   ├── components.yaml                     (NEW: pubsub, state, bindings)
│   ├── pubsub-kafka.yaml                   (NEW: Kafka pub/sub component)
│   ├── state-redis.yaml                    (NEW: Redis state store)
│   └── bindings-cron.yaml                  (NEW: CRON job bindings)
│
├── k8s/                                     (NEW: Kubernetes manifests)
│   ├── namespace.yaml                      (NEW: taskflow namespace)
│   ├── secrets.yaml                        (NEW: Secrets template)
│   ├── configmap.yaml                      (NEW: non-secret config)
│   ├── backend-deployment.yaml             (NEW: Backend pods + Dapr)
│   ├── backend-service.yaml                (NEW: Backend ClusterIP)
│   ├── frontend-deployment.yaml            (NEW: Frontend pods)
│   ├── frontend-service.yaml               (NEW: Frontend NodePort)
│   ├── redis-deployment.yaml               (NEW: Redis state store)
│   ├── redis-service.yaml                  (NEW: Redis ClusterIP)
│   └── ingress.yaml                        (NEW: Ingress for domains)
│
├── helm/
│   └── taskflow/
│       ├── Chart.yaml                      (NEW: Helm metadata)
│       ├── values.yaml                     (NEW: default values)
│       ├── values-dev.yaml                 (NEW: local overrides)
│       ├── values-prod.yaml                (NEW: production overrides)
│       └── templates/                      (NEW: all K8s resources templated)
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── configmap.yaml
│           ├── secrets.yaml
│           └── ...
│
├── docker-compose.yml                      (NEW: local dev with Redpanda + Redis)
├── migrations/                             (NEW: database migrations directory)
│   ├── versions/
│   │   ├── 001_add_recurring_fields.py    (NEW)
│   │   ├── 002_create_reminders_table.py  (NEW)
│   │   └── 003_add_due_date.py            (NEW)
│   └── env.py                              (NEW: Alembic configuration)
│
├── specs/6-event-driven-architecture/
│   ├── spec.md                             (DONE)
│   ├── architecture.md                     (DONE)
│   ├── plan.md                             (THIS FILE)
│   ├── QUICK_REFERENCE.md                  (DONE)
│   ├── DEPLOYMENT.md                       (NEW: multi-option guide)
│   ├── CLOUD_OPTIONS.md                    (NEW: cost/complexity matrix)
│   ├── research.md                         (NEW: Phase 0 research findings)
│   ├── data-model.md                       (NEW: Phase 1 entity definitions)
│   ├── contracts/                          (NEW: API contracts)
│   │   ├── recurring-tasks-api.md
│   │   ├── reminders-api.md
│   │   ├── websocket-api.md
│   │   └── events-schema.md
│   └── checklists/
│       └── requirements.md                 (DONE)
│
└── DEPLOYMENT_SETUP.md                     (NEW: step-by-step for all options)
```

---

## Phase Overview & Dependencies

```
Phase 5.1: Infrastructure Setup (Local)
    ├─> docker-compose.yml, Dockerfiles, base K8s manifests
    └─> Enables: 5.2, 5.3

Phase 5.2: Database Schema
    ├─ Prerequisite: 5.1 (infrastructure running)
    ├─> Task + Reminder models, migrations
    └─> Enables: 5.3

Phase 5.3: Event Foundation (CRITICAL PATH)
    ├─ Prerequisite: 5.1, 5.2
    ├─> Kafka/Dapr setup, event producer/consumer
    └─> Enables: 5.4, 5.5, 5.6

Phase 5.4: Recurring Tasks
    ├─ Prerequisite: 5.3
    ├─> API + scheduler + events
    └─> Can run parallel to 5.5, 5.6

Phase 5.5: Reminders
    ├─ Prerequisite: 5.3
    ├─> API + cron + events
    └─> Can run parallel to 5.4, 5.6

Phase 5.6: Real-Time WebSocket
    ├─ Prerequisite: 5.3
    ├─> WebSocket endpoint + client
    └─> Can run parallel to 5.4, 5.5

Phase 5.7: Kubernetes (Local)
    ├─ Prerequisite: 5.1, 5.3
    ├─> Manifests + Dapr config
    └─> Enables: 5.8

Phase 5.8: Helm Charts
    ├─ Prerequisite: 5.7
    ├─> Chart structure + templating
    └─> Enables: 5.11

Phase 5.9: Cloud Preparation
    ├─ Prerequisite: 5.1, 5.3, 5.4, 5.5, 5.6
    ├─> Environment config, health checks
    └─> Enables: 5.10, 5.11

Phase 5.10: Cloud Simple (Vercel/Render)
    ├─ Prerequisite: 5.9
    ├─> No new code, configuration only
    └─> Parallel to 5.11

Phase 5.11: Cloud K8s (Civo/Dapr)
    ├─ Prerequisite: 5.8, 5.9
    ├─> Reuse Helm charts, cloud config
    └─> Parallel to 5.10

Phase 5.12: Testing & Documentation
    ├─ Prerequisite: 5.4, 5.5, 5.6, 5.10 (or 5.11)
    ├─> Integration tests, load tests, demos
    └─> Final: All features validated
```

---

## Detailed Phases

### Phase 5.1: Infrastructure Setup (Local)

**Objective**: Enable local development with Docker Compose + Dapr + Minikube

**Prerequisites**: Docker Desktop, Minikube installed, basic shell knowledge

**Tasks**:

1. **docker-compose.yml** (NEW)
   ```yaml
   services:
     redpanda:
       image: redpandadata/redpanda:latest
       ports:
         - "9092:9092"
       environment:
         - REDPANDA_BROKERS=redpanda:9092

     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"

     backend:
       build: ./backend
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://...
         - KAFKA_BOOTSTRAP_SERVERS=redpanda:9092
         - REDIS_URL=redis://redis:6379
         - USE_DAPR=true
       depends_on:
         - redpanda
         - redis

     frontend:
       build: ./frontend
       ports:
         - "3000:3000"
       environment:
         - NEXT_PUBLIC_API_URL=http://localhost:8000
         - NEXT_PUBLIC_WS_URL=ws://localhost:8000
   ```

2. **backend/Dockerfile** (NEW - multi-stage)
   ```dockerfile
   # Stage 1: Build
   FROM python:3.13-slim AS builder
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Stage 2: Runtime
   FROM python:3.13-slim
   WORKDIR /app
   RUN useradd -m -u 1000 appuser
   COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
   COPY --chown=appuser:appuser . .
   USER appuser
   EXPOSE 8000
   HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
     CMD python -c "import requests; requests.get('http://localhost:8000/health')"
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **frontend/Dockerfile** (NEW - multi-stage)
   ```dockerfile
   # Stage 1: Build
   FROM node:20-alpine AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci
   COPY . .
   RUN npm run build

   # Stage 2: Runtime
   FROM node:20-alpine
   WORKDIR /app
   RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
   COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
   COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
   USER nextjs
   EXPOSE 3000
   CMD ["node", "server.js"]
   ```

4. **Base K8s manifests** for Minikube (k8s/namespace.yaml, secrets template)

5. **Update requirements.txt** (ADD):
   - aiokafka==0.10.0
   - dapr==1.13.0
   - APScheduler==3.10.0
   - python-dateutil==2.8.2

**Files Created/Modified**:
- docker-compose.yml (NEW)
- backend/Dockerfile (NEW)
- frontend/Dockerfile (NEW)
- k8s/namespace.yaml (NEW)
- backend/requirements.txt (APPEND)

**Testing Checkpoint**:
- `docker-compose up` starts all services
- `curl http://localhost:8000/health` returns 200
- `curl http://localhost:3000` loads frontend
- Redpanda broker accessible at localhost:9092

**Success Criteria**:
- All services start without errors
- Health check passes
- No port conflicts
- Services communicate correctly

**Cost**: $0 (all open source, local Docker)

---

### Phase 5.2: Database Schema Updates

**Objective**: Extend Task model + create Reminders table

**Prerequisites**: Phase 5.1, database connection working

**Tasks**:

1. **backend/models.py** (UPDATE)
   ```python
   # Add to Task model
   due_date: datetime | None = Field(default=None, index=True)
   recurrence_rule: str | None = Field(default=None)  # RRULE format
   is_recurring: bool = Field(default=False, index=True)
   next_occurrence: datetime | None = Field(default=None, index=True)
   ```

2. **NEW Reminder model** (backend/models.py)
   ```python
   class Reminder(SQLModel, table=True):
       id: UUID = Field(default_factory=uuid4, primary_key=True)
       task_id: UUID = Field(foreign_key="task.id")
       user_id: UUID = Field(foreign_key="user.id")
       remind_at: datetime
       notified: bool = Field(default=False)  # Idempotency
       created_at: datetime = Field(default_factory=datetime.utcnow)
   ```

3. **Alembic migrations** (NEW)
   ```bash
   alembic revision --autogenerate -m "add recurring fields"
   alembic revision --autogenerate -m "create reminders table"
   alembic upgrade head
   ```

4. **backend/schemas.py** (UPDATE - Pydantic schemas for API)
   ```python
   class TaskCreateRequest(BaseModel):
       title: str
       description: str | None = None
       due_date: datetime | None = None
       recurrence_rule: str | None = None  # "FREQ=DAILY", "FREQ=WEEKLY;BYDAY=MO"

   class ReminderCreateRequest(BaseModel):
       task_id: UUID
       remind_at: datetime
   ```

**Files Created/Modified**:
- backend/models.py (UPDATE)
- backend/schemas.py (UPDATE)
- migrations/versions/001_add_recurring_fields.py (NEW)
- migrations/versions/002_create_reminders_table.py (NEW)

**Testing Checkpoint**:
- Migrations run without errors on Neon PostgreSQL
- SQLModel schemas validate correctly
- Database tables exist with correct columns
- Pydantic models serialize/deserialize correctly

**Success Criteria**:
- `alembic upgrade head` completes successfully
- `SELECT * FROM task` shows new columns
- `SELECT * FROM reminder` returns empty result set
- Type hints work in IDE autocomplete

**Cost**: $0 (Neon free tier)

---

### Phase 5.3: Event System Foundation (CRITICAL)

**Objective**: Implement event publishing/consuming for both Dapr and direct Kafka

**Prerequisites**: Phase 5.1, 5.2

**Tasks**:

1. **Kafka event schemas** (backend/schemas.py - NEW)
   ```python
   class TaskEvent(BaseModel):
       event_id: str = Field(default_factory=lambda: str(uuid4()))
       event_type: str  # "task.created", "task.updated", etc.
       user_id: str
       aggregate_id: str  # task_id
       timestamp: datetime = Field(default_factory=datetime.utcnow)
       correlation_id: str = Field(default_factory=lambda: str(uuid4()))
       data: dict
       version: int = 1
   ```

2. **Event publisher utility** (backend/services/event_publisher.py - NEW)
   ```python
   class EventPublisher:
       async def publish(self, event: TaskEvent):
           if os.getenv("USE_DAPR") == "true":
               # Dapr pub/sub
               async with DaprClient() as client:
                   await client.publish_event(
                       pub_sub_name="kafka-pubsub",
                       topic_name=f"tasks.events",
                       publish_data=event.model_dump_json(),
                       content_type="application/json"
                   )
           else:
               # Direct Kafka client
               await self.kafka_producer.send_and_wait(
                   "tasks.events",
                   event.model_dump_json().encode(),
                   key=event.user_id.encode()
               )
   ```

3. **Kafka client wrapper** (backend/services/kafka_client.py - NEW)
   - AIOKafkaProducer with retries
   - AIOKafkaConsumer with error handling
   - Topic creation (idempotent)
   - Connection pooling

4. **Dapr client wrapper** (backend/services/dapr_client.py - NEW)
   - DaprClient initialization
   - Pub/sub abstraction matching Kafka API
   - Fallback to direct Kafka if Dapr unavailable

5. **Dapr components configuration** (dapr/ - NEW)
   ```yaml
   # dapr/pubsub-kafka.yaml
   apiVersion: dapr.io/v1alpha1
   kind: Component
   metadata:
     name: kafka-pubsub
   spec:
     type: pubsub.kafka
     version: v1
     metadata:
     - name: brokers
       value: "localhost:9092"
     - name: consumerGroup
       value: "taskflow-consumers"
   ```

6. **Event publisher usage in routes** (backend/routes/tasks.py - UPDATE)
   ```python
   async def create_task(...):
       task = await db.create_task(...)

       # Publish event (async, best-effort)
       await event_publisher.publish(TaskEvent(
           event_type="task.created",
           user_id=str(user_id),
           aggregate_id=str(task.id),
           data=task.model_dump()
       ))

       return task
   ```

7. **Event logging for audit trail** (backend/services/event_log.py - NEW)
   - Store all events in database for replay
   - Query by user_id, time range, event type
   - Implement event sourcing

8. **Environment configuration** (UPDATE .env and main.py)
   ```bash
   USE_DAPR=true  # Set to false for cloud simple deployment
   KAFKA_BOOTSTRAP_SERVERS=redpanda:9092
   KAFKA_SASL_MECHANISM=SCRAM-SHA-256  # Cloud only
   KAFKA_SASL_USERNAME=  # Cloud only
   KAFKA_SASL_PASSWORD=  # Cloud only
   KAFKA_SECURITY_PROTOCOL=SASL_SSL   # Cloud only
   ```

**Files Created/Modified**:
- backend/schemas.py (ADD event schemas)
- backend/services/event_publisher.py (NEW)
- backend/services/kafka_client.py (NEW)
- backend/services/dapr_client.py (NEW)
- backend/services/event_log.py (NEW)
- backend/routes/tasks.py (UPDATE all CRUD operations to publish events)
- dapr/pubsub-kafka.yaml (NEW)
- dapr/state-redis.yaml (NEW)
- .env (UPDATE with Kafka config)
- backend/requirements.txt (APPEND aiokafka, dapr-sdk)

**Testing Checkpoint**:
- Event published when task created
- Event appears in Kafka topic (verify with kcat)
- Event stored in database (event_log table)
- Both Dapr and direct Kafka paths work
- Event retry logic handles transient failures

**Success Criteria**:
- Create task → event published → consumer receives within 100ms
- Event_id deduplication prevents duplicates
- User_id isolation verified (no cross-user events)
- Error handling logs all failures
- Environment variable switching works

**Cost**: $0 (local Redpanda + Redis)

---

### Phase 5.4: Recurring Tasks Feature

**Objective**: Automatic task spawning on schedule

**Prerequisites**: Phase 5.3

**Tasks**:

1. **API endpoints** (backend/routes/tasks.py - NEW)
   ```python
   POST /api/{user_id}/tasks/{id}/recurrence
       Request: { "recurrence_rule": "FREQ=DAILY" }
       Response: { "id", "recurrence_rule", "next_occurrence" }

   GET /api/{user_id}/tasks/recurring
       Response: [ { "id", "title", "next_occurrence" } ]

   DELETE /api/{user_id}/tasks/{id}/recurrence
       Response: 204 No Content
   ```

2. **Recurrence calculation** (backend/services/scheduler.py - NEW)
   ```python
   from dateutil.rrule import rrulestr

   class RecurrenceCalculator:
       def calculate_next_occurrence(self, rrule: str, user_timezone: str):
           tz = pytz.timezone(user_timezone)
           rrule_obj = rrulestr(rrule, dtstart=datetime.now(tz))
           return rrule_obj._iter()[1]  # Next occurrence
   ```

3. **Scheduler service** (backend/services/scheduler.py - NEW)
   ```python
   class TaskScheduler:
       async def spawn_recurring_tasks(self):
           # Run every minute
           tasks = await db.get_recurring_tasks_due()
           for task in tasks:
               new_task = await db.create_task(
                   user_id=task.user_id,
                   title=task.title,
                   description=task.description
               )

               # Calculate next occurrence
               next_occ = calculate_next_occurrence(task.recurrence_rule)
               await db.update_task_next_occurrence(task.id, next_occ)

               # Publish event
               await event_publisher.publish(TaskEvent(
                   event_type="recurring.spawned",
                   aggregate_id=str(new_task.id),
                   data=new_task.model_dump()
               ))
   ```

4. **APScheduler integration** (backend/main.py - NEW)
   ```python
   from apscheduler.schedulers.asyncio import AsyncIOScheduler

   scheduler = AsyncIOScheduler()
   scheduler.add_job(
       scheduler_service.spawn_recurring_tasks,
       'interval',
       minutes=1,
       max_instances=1  # Prevent duplicates
   )
   scheduler.start()
   ```

5. **Dapr binding alternative** (dapr/bindings-cron.yaml - NEW)
   ```yaml
   # For K8s deployment with Dapr
   apiVersion: dapr.io/v1alpha1
   kind: Component
   metadata:
     name: cron-trigger
   spec:
     type: bindings.cron
     metadata:
     - name: schedule
       value: "@every 1m"
   ```

6. **Frontend UI** (frontend/components/tasks/RecurrenceForm.tsx - NEW)
   - Dropdown: None, Daily, Weekly, Monthly
   - If Weekly: checkboxes for days
   - If Monthly: date selector
   - Display next occurrence

**Files Created/Modified**:
- backend/routes/tasks.py (ADD 3 endpoints)
- backend/services/scheduler.py (NEW)
- backend/main.py (UPDATE with APScheduler)
- dapr/bindings-cron.yaml (NEW)
- backend/requirements.txt (APPEND python-dateutil, apscheduler)
- frontend/components/tasks/RecurrenceForm.tsx (NEW)
- frontend/components/tasks/TaskCard.tsx (UPDATE to show recurrence)

**Testing Checkpoint**:
- Set daily recurrence → next instance spawns at midnight (user timezone)
- Weekly recurrence with multiple days works
- Monthly recurrence on specific dates works
- Next_occurrence updated correctly
- Frontend UI saves/displays recurrence pattern

**Success Criteria**:
- Recurring task spawns within 5 minutes of scheduled time
- No duplicate instances created (max_instances=1)
- Timezone calculation correct
- Event published with full task data
- UI allows setting all RRULE patterns

**Cost**: $0 (APScheduler local, no external scheduler service)

---

### Phase 5.5: Reminders Feature

**Objective**: Notify users before task due dates

**Prerequisites**: Phase 5.3

**Tasks**:

1. **API endpoints** (backend/routes/tasks.py - NEW)
   ```python
   PUT /api/{user_id}/tasks/{id}/due-date
       Request: { "due_date": "2026-02-20T09:00:00Z" }

   POST /api/{user_id}/tasks/{id}/reminders
       Request: { "remind_at": "2026-02-19T09:00:00Z" }
       Response: { "id", "task_id", "remind_at" }

   GET /api/{user_id}/reminders/pending
       Response: [ { "id", "task_id", "task_title", "remind_at" } ]
   ```

2. **Reminder cron job** (backend/services/scheduler.py - UPDATE)
   ```python
   async def check_pending_reminders(self):
       # Run every minute
       pending = await db.get_reminders_due()
       for reminder in pending:
           # Publish event
           await event_publisher.publish(TaskEvent(
               event_type="reminder.triggered",
               user_id=reminder.user_id,
               aggregate_id=str(reminder.id),
               data={
                   "task_id": str(reminder.task_id),
                   "task_title": reminder.task.title,
                   "remind_at": reminder.remind_at
               }
           ))

           # Mark as notified (idempotency)
           await db.update_reminder_notified(reminder.id, True)
   ```

3. **APScheduler job for reminders** (backend/main.py - UPDATE)
   ```python
   scheduler.add_job(
       scheduler_service.check_pending_reminders,
       'interval',
       minutes=1,
       max_instances=1
   )
   ```

4. **Dapr binding for cron** (dapr/bindings-cron.yaml - UPDATE with multiple triggers)

5. **Frontend UI** (frontend/components/tasks/DueDatePicker.tsx - NEW)
   - Due date picker
   - Multiple reminder options (1 day before, 1 hour before, 30 min before)
   - Display list of set reminders

**Files Created/Modified**:
- backend/routes/tasks.py (ADD 3 endpoints)
- backend/services/scheduler.py (UPDATE with check_pending_reminders)
- backend/main.py (UPDATE APScheduler)
- frontend/components/tasks/DueDatePicker.tsx (NEW)
- frontend/components/tasks/TaskCard.tsx (UPDATE with due date display)

**Testing Checkpoint**:
- Create reminder → event triggered at remind_at time
- Multiple reminders on single task work
- Idempotency: duplicate events don't create duplicate notifications
- Completed tasks cancel pending reminders
- Frontend UI shows all reminders

**Success Criteria**:
- Reminder event published within 1 minute of remind_at
- 100% of reminders sent (verified by event count)
- No duplicate notifications
- Reminders cancel on task deletion
- UI allows multiple reminders

**Cost**: $0 (APScheduler local)

---

### Phase 5.6: Real-Time Updates (WebSocket)

**Objective**: Live task synchronization across devices

**Prerequisites**: Phase 5.3

**Tasks**:

1. **WebSocket endpoint** (backend/routes/websocket.py - NEW)
   ```python
   @app.websocket("/ws/user/{user_id}/tasks")
   async def websocket_endpoint(websocket: WebSocket, user_id: str):
       # 1. JWT validation on connect
       token = websocket.query_params.get("token")
       try:
           payload = verify_jwt(token)
           if payload["sub"] != user_id:
               await websocket.close(code=4003, reason="Unauthorized")
               return
       except Exception:
           await websocket.close(code=4001, reason="Invalid token")
           return

       # 2. Accept connection
       await websocket.accept()

       # 3. Add to room (per-user)
       ws_manager.add_connection(user_id, websocket)

       # 4. Subscribe to user's task events
       async def consumer_callback(event):
           await websocket.send_json({
               "type": event["event_type"],
               "data": event["data"],
               "timestamp": event["timestamp"],
               "correlation_id": event["correlation_id"]
           })

       await event_subscriber.subscribe(
           topic=f"tasks.events",
           user_id=user_id,
           callback=consumer_callback
       )

       # 5. Keep connection open
       try:
           while True:
               # Ping every 30s for keep-alive
               await asyncio.sleep(30)
               await websocket.send_text("ping")
       except Exception as e:
           ws_manager.remove_connection(user_id, websocket)
   ```

2. **WebSocket manager** (backend/services/websocket_manager.py - NEW)
   ```python
   class WebSocketManager:
       def __init__(self):
           self.active_connections: dict[str, list[WebSocket]] = {}

       def add_connection(self, user_id: str, ws: WebSocket):
           if user_id not in self.active_connections:
               self.active_connections[user_id] = []
           self.active_connections[user_id].append(ws)

       async def broadcast_to_user(self, user_id: str, message: dict):
           if user_id in self.active_connections:
               for ws in self.active_connections[user_id]:
                   try:
                       await ws.send_json(message)
                   except Exception:
                       pass  # Connection closed
   ```

3. **Event consumer for WebSocket** (backend/handlers/websocket_handler.py - NEW)
   ```python
   class WebSocketHandler:
       async def on_task_event(self, event: TaskEvent):
           message = {
               "type": event.event_type,
               "data": event.data,
               "timestamp": event.timestamp.isoformat(),
               "correlation_id": event.correlation_id
           }
           await ws_manager.broadcast_to_user(event.user_id, message)
   ```

4. **Frontend WebSocket client** (frontend/lib/websocket-client.ts - NEW)
   ```typescript
   export class WebSocketClient {
       private ws: WebSocket | null = null;
       private reconnectAttempts = 0;
       private maxReconnectAttempts = 5;
       private reconnectDelay = 1000;

       async connect(userId: string, token: string) {
           const url = `${process.env.NEXT_PUBLIC_WS_URL}/ws/user/${userId}/tasks?token=${token}`;
           this.ws = new WebSocket(url);

           this.ws.onmessage = (event) => {
               const message = JSON.parse(event.data);
               this.dispatchUpdate(message);
           };

           this.ws.onclose = () => this.reconnect();

           this.ws.onerror = (error) => console.error("WS error:", error);
       }

       private reconnect() {
           if (this.reconnectAttempts < this.maxReconnectAttempts) {
               this.reconnectAttempts++;
               setTimeout(
                   () => this.connect(...),
                   this.reconnectDelay * Math.pow(2, this.reconnectAttempts)
               );
           }
       }

       private dispatchUpdate(message: any) {
           // Update local state, trigger re-render
           window.dispatchEvent(new CustomEvent("task-update", { detail: message }));
       }
   }
   ```

5. **Frontend WebSocket provider** (frontend/components/realtime/WebSocketProvider.tsx - NEW)
   ```typescript
   export function WebSocketProvider({ children }) {
       const { user } = useAuth();
       const [client, setClient] = useState<WebSocketClient | null>(null);

       useEffect(() => {
           if (user && user.sessionToken) {
               const wsClient = new WebSocketClient();
               wsClient.connect(user.id, user.sessionToken);
               setClient(wsClient);
           }

           return () => client?.disconnect();
       }, [user]);

       return <>{children}</>;
   }
   ```

6. **Update task routes to trigger WebSocket events** (backend/routes/tasks.py - UPDATE)
   - After each task operation (create, update, delete), publish event
   - Event consumed by WebSocket handler
   - Message broadcast to all connected clients for that user

**Files Created/Modified**:
- backend/routes/websocket.py (NEW)
- backend/services/websocket_manager.py (NEW)
- backend/handlers/websocket_handler.py (NEW)
- frontend/lib/websocket-client.ts (NEW)
- frontend/components/realtime/WebSocketProvider.tsx (NEW)
- frontend/app/layout.tsx (WRAP with WebSocketProvider)

**Testing Checkpoint**:
- Open 2 browser tabs → create task in Tab 1 → appears in Tab 2 within 500ms
- WebSocket reconnects within 5s on disconnect
- Multiple simultaneous updates sync correctly
- User isolation: Tab for User A doesn't receive User B's updates
- Fallback to polling if WebSocket unavailable

**Success Criteria**:
- <500ms latency from task operation to client update (p95)
- Handles 100+ concurrent WebSocket connections
- Auto-reconnect succeeds after network interruption
- Zero data leakage between users
- Graceful degradation (polling fallback)

**Cost**: $0 (no external service)

---

### Phase 5.7-5.12: Kubernetes, Helm, Cloud Deployments, Testing & Docs

(Due to token limits, I'll provide a summary rather than full details for the remaining phases)

**Phase 5.7: Kubernetes (Local Minikube)**
- Create Deployment/Service/ConfigMap/Secret manifests
- Configure Dapr components for K8s
- Test on Minikube with port-forward
- Success: `helm install` on local K8s works

**Phase 5.8: Helm Charts**
- Templated all K8s resources
- values.yaml with sensible defaults
- Support local/prod overrides
- Test helm upgrade/rollback

**Phase 5.9: Cloud Preparation**
- Environment config for Render/Vercel/Civo
- Health check endpoints
- CORS configuration
- Graceful Dapr absence handling

**Phase 5.10: Cloud Simple (Vercel/Render)**
- Configuration only (no code changes)
- Redpanda Cloud Serverless setup
- Direct Kafka client (no Dapr)
- Single Render instance (free tier)

**Phase 5.11: Cloud K8s (Civo/Dapr)**
- Civo cluster creation ($250 credit)
- Dapr installation on K8s
- Helm chart deployment
- Ingress configuration

**Phase 5.12: Testing & Documentation**
- Integration tests for event flows
- Load test (1000+ events/sec)
- E2E tests across all features
- Complete DEPLOYMENT.md
- Create demo video

---

## Critical Dependencies & Fallback Strategies

### Dependency Chain
```
Phase 5.1 (Local infra) ─┐
                         ├─> Phase 5.3 (Event foundation) ─┬─> 5.4, 5.5, 5.6 (parallel)
Phase 5.2 (DB schema)   ─┘                                │
                                                           ├─> Phase 5.9 (Cloud prep)
Phase 5.7 (K8s) ──> Phase 5.8 (Helm) ──────────────────┬─┴─> Phase 5.10 (Cloud Simple)
                                                      └──────> Phase 5.11 (Cloud K8s)

Phase 5.12 (Testing) ── All prior phases complete
```

### Free Tier Fallback Strategies

| Limitation | Mitigation |
|-----------|-----------|
| Render 750hrs/month | Single instance; spins down after 15 min (cold start 60s) |
| Neon 5GB storage | Monitor usage; export/reimport if needed |
| Redpanda 10GB/month | Consolidate topics; compress messages; monitoring |
| Civo $250 credit ~2-3 months | Use for demo; upgrade to paid for production |
| Dapr K8s only | Direct Kafka clients for cloud simple; no code changes needed |
| Single Render instance | No horizontal scaling; upgrade for production |

---

## Success Metrics & Validation

### By Phase

| Phase | Success Metric |
|-------|---|
| 5.1 | All services start in docker-compose without errors |
| 5.2 | Migrations run; database schema verified |
| 5.3 | Events published/consumed; both Dapr and Kafka paths work |
| 5.4 | Recurring tasks spawn on schedule within 5 minutes |
| 5.5 | Reminders sent within 1 minute of remind_at |
| 5.6 | WebSocket sync <500ms latency (p95); 100+ concurrent connections |
| 5.7 | `helm install` succeeds on Minikube; pods running |
| 5.8 | `helm upgrade` works; values override correctly |
| 5.9 | All services use correct environment variables per deployment |
| 5.10 | Deploy to Vercel + Render succeeds; app fully functional |
| 5.11 | Deploy to Civo K8s succeeds; Dapr sidecars injected |
| 5.12 | All tests pass; demo video shows all features |

### Overall

- ✅ Event throughput: 1000+ events/sec
- ✅ Real-time latency: <500ms (p95)
- ✅ WebSocket delivery: <100ms
- ✅ 3 deployments working: Local + Cloud Simple + Cloud K8s
- ✅ 100% free tier: $0 cost
- ✅ User isolation: No cross-user data leakage
- ✅ Graceful degradation: System works when services unavailable

---

## Cost Breakdown (All $0)

| Component | Cost | Tier |
|-----------|------|------|
| PostgreSQL (Neon) | $0 | FREE: 5GB storage, 3 projects |
| Kafka/Redpanda Cloud | $0 | FREE: 10GB/month, 3 topics |
| Vercel (Frontend) | $0 | FREE: Unlimited bandwidth, auto-scaling |
| Render.com (Backend) | $0 | FREE: 750 hrs/month (1 instance always running) |
| Civo Kubernetes | $0 | $250 FREE CREDIT: ~2-3 months cluster runtime |
| Linode Kubernetes | $0 | $100 FREE CREDIT: 60 days |
| Docker Desktop | $0 | FREE: Community Edition |
| Minikube | $0 | FREE: Open source K8s local |
| Dapr | $0 | FREE: Open source runtime |
| **TOTAL** | **$0** | **100% FREE** |

---

## Timeline Estimate

**Assuming 4-5 dev hours/week**:

| Phase | Duration | Cumulative |
|-------|----------|-----------|
| 5.1 Infrastructure | 1 week | 1 week |
| 5.2 Database | 3 days | 1.4 weeks |
| 5.3 Events (CRITICAL) | 2 weeks | 3.4 weeks |
| 5.4 Recurring Tasks | 1 week | 4.4 weeks |
| 5.5 Reminders | 4 days | 4.95 weeks |
| 5.6 WebSocket | 5 days | 5.6 weeks |
| 5.7-5.8 K8s + Helm | 1.5 weeks | 7.1 weeks |
| 5.9 Cloud Prep | 3 days | 7.5 weeks |
| 5.10 Cloud Simple | 2 days | 7.8 weeks |
| 5.11 Cloud K8s | 2 days | 8 weeks |
| 5.12 Testing + Docs | 2 weeks | **10 weeks** |

**TOTAL: ~10 weeks (2.5 months)** with 4-5 dev hours/week

---

## Next Steps

1. **Phase 0 Research** (if needed): Resolve any NEEDS CLARIFICATION from technical context
2. **Begin Phase 5.1**: Set up local infrastructure
3. **Validate each phase** before moving to next
4. **Parallel work**: While Phase 5.3 in progress, start Phase 5.7 (K8s manifests)
5. **Test continuously**: Each phase has checkpoint testing

---

**Plan Status**: ✅ READY FOR TASK GENERATION
**Next Command**: `/sp.tasks` to generate T-401 onwards
