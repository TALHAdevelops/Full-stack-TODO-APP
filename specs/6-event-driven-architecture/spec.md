# Phase 5: Distributed Cloud-Native Event-Driven Todo System

**Feature Branch**: `6-event-driven-architecture`
**Created**: 2026-02-14
**Status**: Specification Draft
**Input**: Phase 5 requirements with event streaming, Dapr integration, recurring tasks, reminders, real-time updates

## User Scenarios & Testing (Mandatory)

### User Story 1: Create Task with Real-Time Sync (Priority: P1 - MVP)

**Actor**: Authenticated task user across multiple devices

**Narrative**: When a user creates a task on their desktop, that task appears instantly on their mobile device without requiring a page refresh. The system reliably synchronizes task state across all connected clients.

**Why this priority**: Real-time synchronization is the core value proposition of Phase 5, differentiating it from traditional REST-only architectures. Enables seamless multi-device workflows.

**Independent Test**: Deploy Phase 5 with WebSocket support; open task dashboard on two browsers; create task in one browser; verify instant appearance in second browser within 500ms.

**Acceptance Scenarios**:

1. **Given** user is logged in on two browser tabs, **When** user creates task in Tab 1, **Then** task appears in Tab 2 within 500ms without refresh
2. **Given** task event published to Kafka, **When** WebSocket client connected, **Then** client receives event and can display to user
3. **Given** WebSocket connection drops, **When** reconnection succeeds, **Then** user receives missed task events (no data loss)
4. **Given** Kafka unavailable, **When** task creation attempted, **Then** task created locally and queued for later sync (graceful degradation)

---

### User Story 2: Recurring Tasks with Automatic Generation (Priority: P1 - MVP)

**Actor**: User with recurring workflows (daily standup notes, weekly reports, monthly reviews)

**Narrative**: User creates a recurring task (e.g., "Weekly sync meeting every Monday at 9 AM"). System automatically generates a new task instance each Monday at 9 AM without user intervention. User can complete recurring tasks individually; next instance generates independently.

**Why this priority**: Recurring tasks eliminate manual task creation for routine activities, directly increasing user productivity. High-frequency request from todo app users.

**Independent Test**: Create recurring task with daily recurrence; wait for scheduled time; verify new task instance auto-created; verify original task completion doesn't block next instance.

**Acceptance Scenarios**:

1. **Given** user creates recurring task with daily recurrence, **When** next scheduled time arrives, **Then** new task instance created automatically
2. **Given** recurring task created for specific timezone, **When** scheduled time evaluated, **Then** time calculated in user's timezone (not UTC)
3. **Given** recurring task spawns next instance, **When** event published, **Then** WebSocket clients notified of new task
4. **Given** recurring task completed, **When** next instance due, **Then** next instance created independently (completion doesn't block recurrence)

---

### User Story 3: Task Reminders Before Due Date (Priority: P2)

**Actor**: User who needs proactive notifications for upcoming deadlines

**Narrative**: User sets a due date on a task and configures a reminder (e.g., "Remind me 1 day before"). System sends notification when reminder time arrives. Multiple reminders on single task supported (e.g., 1 day before + 1 hour before).

**Why this priority**: Reminders prevent missed deadlines and increase task completion rate. Standard feature in todo apps; enables time-sensitive workflows.

**Independent Test**: Create task with due date 24 hours from now; set reminder for 1 day before; verify reminder notification sent exactly 24 hours from creation time.

**Acceptance Scenarios**:

1. **Given** task with due date and reminder set, **When** reminder time arrives, **Then** notification sent to user (via WebSocket push)
2. **Given** multiple reminders on single task, **When** each reminder time arrives, **Then** each reminder notified independently
3. **Given** reminder already sent, **When** task completed, **Then** pending reminders cancelled
4. **Given** reminder notification sent, **When** notification received, **Then** reminder marked as notified (idempotency check prevents duplicate notifications)

---

### User Story 4: Event History & Audit Trail (Priority: P2)

**Actor**: Users and administrators who need to understand task history

**Narrative**: All task state changes (created, updated, completed, deleted) generate immutable events stored in Kafka. Users can trace task history; administrators can audit system events for compliance and debugging.

**Why this priority**: Audit trail enables debugging of event processing issues; meets compliance requirements for data accountability; enables potential undo/redo features in future.

**Independent Test**: Create task, update title, mark complete, delete task; retrieve event history; verify all events present in correct chronological order with full context.

**Acceptance Scenarios**:

1. **Given** task created, updated, and completed, **When** event history retrieved, **Then** all 3 events present in correct order with timestamps
2. **Given** event published, **When** event retrieved from history, **Then** all context preserved (user_id, original values, new values, correlation_id)
3. **Given** events stored in Kafka, **When** topic replayed, **Then** exact same sequence of events reproduced (event sourcing capability)
4. **Given** multiple users interacting with tasks, **When** events retrieved, **Then** each event includes user_id (user isolation verified)

---

## Requirements (Mandatory)

### Functional Requirements

**FR-001**: System MUST emit events for all task state changes (created, updated, completed, deleted, due_date changed, recurrence spawned)

**FR-002**: System MUST support recurring task patterns: none, daily, weekly (specific days), monthly (specific date)

**FR-003**: System MUST automatically generate new task instances on recurrence schedule based on user timezone

**FR-004**: System MUST support multiple reminders per task with configurable lead times (1 day before, 1 hour before, etc.)

**FR-005**: System MUST publish reminder notifications to WebSocket when reminder time arrives

**FR-006**: System MUST provide real-time updates to connected clients via WebSocket when task state changes

**FR-007**: System MUST support graceful degradation when event streaming unavailable (fallback to database queue)

**FR-008**: System MUST maintain event immutability (events never modified after creation)

**FR-009**: System MUST provide event replay capability for audit trail and debugging

**FR-010**: System MUST validate all WebSocket connections with JWT authentication

**FR-011**: System MUST enforce user isolation on all event subscriptions (users only receive their own events)

**FR-012**: System MUST support three deployment options: Local Minikube+Dapr, Cloud Simple (Vercel/Render), Cloud K8s (Civo/Linode)

**FR-013**: System MUST implement graceful degradation when Dapr unavailable (direct Kafka clients as fallback)

### Key Entities

**Task** (Extended):
- `id` (UUID): Unique identifier
- `user_id` (FK): User who owns task
- `title` (string): Task title
- `description` (text, optional): Task description
- `completed` (boolean): Completion status
- `due_date` (timestamp, optional): When task is due
- `recurrence_rule` (string, optional): RRULE format (e.g., "FREQ=DAILY", "FREQ=WEEKLY;BYDAY=MO")
- `is_recurring` (boolean): Whether task is recurring
- `next_occurrence` (timestamp, optional): When next recurrence should spawn
- `created_at` (timestamp): Creation time
- `updated_at` (timestamp): Last update time

**Reminder** (New):
- `id` (UUID): Unique identifier
- `task_id` (FK): Task this reminder belongs to
- `user_id` (FK): User who owns reminder
- `remind_at` (timestamp): When reminder should trigger
- `notified` (boolean): Whether reminder already sent
- `created_at` (timestamp): Creation time

**Event** (Immutable record in Kafka):
- `event_id` (UUID): Unique event identifier
- `event_type` (string): "task.created", "task.updated", "task.deleted", "task.completed", "task.uncompleted", "recurring.spawned", "reminder.triggered"
- `user_id` (string): User ID for isolation
- `aggregate_id` (UUID): task_id or conversation_id
- `timestamp` (ISO-8601): When event occurred
- `data` (JSON): Event payload with changed values
- `version` (integer): For replay sequencing
- `correlation_id` (UUID): Links related events across services

**WebSocket Message** (Client ←→ Server):
```json
{
  "type": "task.created|updated|deleted|completed",
  "data": { ... },
  "timestamp": "2026-02-14T15:30:00Z",
  "correlation_id": "uuid"
}
```

---

## Success Criteria (Mandatory)

### Measurable Outcomes

**SC-001**: Users see task updates on all connected devices within 500ms of creation (real-time perception)

**SC-002**: Recurring tasks spawn automatically within 5 minutes of scheduled time (scheduling accuracy)

**SC-003**: Reminder notifications sent within 1 minute of scheduled reminder time (notification reliability)

**SC-004**: System processes 1000+ events per second without degradation (throughput)

**SC-005**: System maintains <100ms event latency from publication to WebSocket delivery (p95 latency)

**SC-006**: WebSocket reconnection completes within 5 seconds on network interruption (resilience)

**SC-007**: Event history reconstructs complete task state when replayed from Kafka (audit trail integrity)

**SC-008**: 100% of events include user_id and correlation_id (traceability)

**SC-009**: System gracefully handles Kafka unavailability with fallback to database queue (graceful degradation)

**SC-010**: Deployment options A and B launch from GitHub repo to production within 15 minutes (deployment simplicity)

**SC-011**: Free tier resources (Neon PostgreSQL, Redpanda Cloud Serverless, Vercel/Render, Civo/$250 credit) sufficient for 1000 active users

**SC-012**: Task completion workflow remains responsive even with 100+ concurrent WebSocket connections per instance (scalability)

---

## Assumptions

1. **Event Ordering**: Events for single user processed in order (Kafka partitioning by user_id ensures this)
2. **Time Zone**: User timezone stored and used for recurrence calculations; system uses UTC internally
3. **Recurring Task Limits**: System supports RRULE subset (no complex exclusions); unlimited future instances per task
4. **Reminder Precision**: Reminders sent "around" scheduled time, not exact (within 1 minute acceptable)
5. **WebSocket Fallback**: If WebSocket unavailable, frontend falls back to HTTP polling every 30 seconds
6. **Free Tier Sufficiency**: Civo/Linode $250/$100 credits sufficient for 2-3 month demo period; production requires paid tier
7. **Dapr Optional**: Dapr simplifies local development; cloud deployments work without it (direct Kafka clients)
8. **Event Immutability**: Events never deleted or modified; corrections published as new "correction" events
9. **User Context**: All operations implicitly include current user from JWT token

---

## Edge Cases

- **Simultaneous Task Update**: Two users update different properties of shared/non-shared task simultaneously → Last-write-wins (later update_at timestamp wins)
- **Recurring Task Completion**: User completes recurring task; next instance still spawns independently
- **Reminder After Deletion**: Task deleted before reminder time → Reminder cancels; no notification sent
- **WebSocket During Kafka Outage**: User connects WebSocket while Kafka down → WebSocket accepts connection but queues updates for later delivery when Kafka recovers
- **Timezone Change**: User changes timezone → Existing recurring tasks recalculate next_occurrence based on new timezone
- **Event Replay During Active Updates**: Admin replays event history → New events published simultaneously → Last-write-wins applied
- **Dapr Sidecar Crash**: Dapr sidecar restarts → Backend automatically reconnects and resubscribes to topics
- **Reminder Duplication**: Reminder triggered twice due to race condition → Idempotency check (notified flag) prevents duplicate notifications

---

## Test Strategy

### Unit Tests
- RRULE parsing for all supported patterns
- Event deduplication (event_id collision detection)
- Timezone handling for recurrence calculations
- Reminder time comparisons in user timezone

### Integration Tests
- Task creation → event published → WebSocket clients notified (full flow)
- Recurring task spawning on schedule
- Multiple reminders on single task
- Graceful degradation when Kafka unavailable
- Event replay reconstructs task state

### End-to-End Tests
- Multi-user concurrent updates with real-time sync
- Recurring task generation at exact scheduled time
- Reminder notification delivery at exact time
- WebSocket reconnection recovery
- Cross-browser real-time sync (Tab A create → Tab B sees instantly)

### Performance Tests
- 1000+ events/second throughput
- <500ms end-to-end event delivery latency
- 100+ concurrent WebSocket connections per instance
- 5-minute recurrence accuracy over 1 week

---

## Deployment Considerations

### Local Development
- Docker Compose with Redpanda, Redis, Backend, Frontend
- Dapr sidecar attached to backend for testing
- Full event streaming locally; no external dependencies

### Cloud Option A (Simple - Vercel/Render)
- No Dapr (direct Kafka clients)
- Single backend instance on Render (no horizontal scaling)
- Simpler deployment; limited scalability
- Suitable for demo/portfolio

### Cloud Option B (Kubernetes - Civo/Linode)
- Full K8s with Dapr
- Multiple backend replicas
- Full cloud-native architecture
- Demonstrates infrastructure skills

---

## Scope Boundaries

**Included**:
- Event-driven task operations (CRUD + state transitions)
- Recurring task scheduling and spawning
- Reminder notifications via WebSocket
- Real-time client synchronization
- Dapr integration for local development
- Three deployment options

**Excluded**:
- In-app notification center (out of scope; notifications sent via WebSocket only)
- Email/SMS reminders (WebSocket only for Phase 5)
- Advanced RRULE patterns (EXDATE, EXRULE, complex recurrences)
- Event analytics dashboard (audit trail stored, not visualized)
- Message queue persistence beyond Kafka retention (7 days standard)
- Dapr for cloud deployments (cloud uses direct Kafka clients)
