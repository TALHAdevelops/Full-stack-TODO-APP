# Phase 5 Architecture: Distributed Event-Driven System

**Purpose**: Comprehensive architecture design for Phase 5 event-driven todo system across all deployment options

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                              │
├──────────────────────────────┬──────────────────────────────────────┤
│  Frontend (Next.js)          │  API Gateway / Load Balancer         │
│  - Dashboard with real-time  │  - Route to backend instances        │
│    task updates              │  - WebSocket upgrade handling        │
│  - WebSocket with auto-      │  - JWT validation                    │
│    reconnect (500ms backoff) │                                      │
└──────────────────┬───────────┴──────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │ HTTP / WebSocket    │
        │ (TLS/SSL in prod)   │
        │                     │
┌───────▼──────────────────────▼──────────────────────────────────────┐
│                         SERVICE LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│  Backend (FastAPI) - Multiple Replicas                             │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ REST API Routes                                                │ │
│  │ - POST /api/{user_id}/tasks                                   │ │
│  │ - PUT /api/{user_id}/tasks/{id}                               │ │
│  │ - DELETE /api/{user_id}/tasks/{id}                            │ │
│  │ - POST /api/{user_id}/tasks/{id}/recurrence                  │ │
│  │ - POST /api/{user_id}/tasks/{id}/reminders                   │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │ WebSocket Endpoint                                             │ │
│  │ - GET /ws/user/{user_id}/tasks                                │ │
│  │   • JWT validation on connect                                 │ │
│  │   • Subscribe to user task events                             │ │
│  │   • Auto-reconnect on client disconnect                       │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │ Event Publishing                                               │ │
│  │ - Publish events after DB operation                           │ │
│  │ - Partition by user_id (ordering guarantee)                   │ │
│  │ - Graceful fallback to DB queue if Kafka unavailable          │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │ Event Consumers                                                │ │
│  │ - Subscribe to task.events topic                              │ │
│  │ - Subscribe to reminders.events topic                         │ │
│  │ - Idempotent processing (event_id deduplication)              │ │
│  │ - Publish to WebSocket connected clients                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Scheduler Service - Single Replica                               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ - APScheduler or Dapr Bindings for cron jobs                  │ │
│  │ - Runs every minute: check for recurring task triggers        │ │
│  │ - Spawn new task instances based on recurrence_rule           │ │
│  │ - Check for reminders due in next 1 minute                    │ │
│  │ - Publish reminder.triggered events to Kafka                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────┬────────────────┘
                  │                                   │
        ┌─────────▼──────────┐         ┌─────────────▼──────────┐
        │ Kafka / Redpanda   │         │  PostgreSQL (Neon)     │
        │                    │         │  - Tasks table         │
        │ Topics:            │         │  - Reminders table     │
        │ - tasks.events     │         │  - Event queue         │
        │ - reminders.events │         │  - Conversation history│
        │ - task-updates     │         │                        │
        │                    │         │ Connection Pool        │
        │ Partitioned by:    │         │ (handles multiple      │
        │ - user_id (order)  │         │  backend replicas)     │
        │                    │         │                        │
        │ Retention:         │         │                        │
        │ - 7 days standard  │         │                        │
        │                    │         │                        │
        │ Brokers:           │         │                        │
        │ Local: localhost   │         │ Authorization:         │
        │ Cloud: Redpanda    │         │ - Connection string    │
        │        Cloud       │         │   in K8s Secret        │
        │        Serverless  │         │                        │
        └────────────────────┘         └────────────────────────┘
```

---

## Service Communication Patterns

### 1. Task Creation Flow (HTTP → Event → WebSocket)

```
User (Desktop)     Backend Instance 1    Kafka              User (Mobile)
    │                                                           │
    ├─ POST /api/user/tasks ──────────────────────────────────>│
    │                                                           │
    │                 ├─ Validate JWT                           │
    │                 ├─ Create task in DB                      │
    │                 ├─ Publish task.created event ──────────>│
    │                 │                                         │
    │                 │    ┌─────────────────────────────────────────┐
    │                 │    │ Consumer (Backend Instance 2)           │
    │                 │    ├─ Receives task.created event           │
    │                 │    ├─ Notifies WebSocket subscribers ──────>│
    │                 │    │        (if user has active connection) │
    │<─ 201 Created ──┤    │                                         │
    │ {task}          │    └─────────────────────────────────────────┘
    │                 │
    └─ Updates UI    │
                     │
                     └─ Publishes to WebSocket:
                        {
                          "type": "task.created",
                          "data": {...},
                          "timestamp": "...",
                          "correlation_id": "..."
                        }

    Mobile receives event within 500ms (p95)
    └─ Updates task list automatically
```

### 2. Recurring Task Spawning Flow (Scheduler → Event → WebSocket)

```
Scheduler Service      Kafka               Backend Instance 1    User Clients
     │                                             │                    │
     ├─ 1-minute tick ──────────────────────────>│                    │
     │                                             │                    │
     ├─ Query recurring tasks due                 │                    │
     │  (next_occurrence <= now)                  │                    │
     │                                             │                    │
     ├─ For each: calculate next_occurrence       │                    │
     │                                             │                    │
     ├─ Create new task instance                  │                    │
     │                                             │                    │
     ├─ Publish recurring.spawned event ────────>│                    │
     │                                   │        │                    │
     │                          Consumer processes│                    │
     │                          Notifies WebSocket├─ task.created ────>│
     │                                            │                    │
     │                                            └─ Real-time sync ──>│
     │                                                                  │
     └─ Update next_occurrence for next cycle
```

### 3. Reminder Notification Flow (Scheduler → Event → WebSocket)

```
Scheduler Service      Kafka               Backend Instance      WebSocket
     │                                            │                  │
     ├─ Every minute:                            │                  │
     │  Check reminders due in next 60s          │                  │
     │                                            │                  │
     ├─ Publish reminder.triggered ─────────────>│                  │
     │  for each due reminder                    │                  │
     │                                     Consumer processes        │
     │                              Mark reminder notified           │
     │                              Publish to WebSocket ───────────>│
     │                                                               │
     │                                     {                        │
     │                                       type: "reminder",      │
     │                                       data: {...}           │
     │                                     }                        │
     │                                                               │
     └─ Delete pending notification              Client notifies user
```

### 4. Event-Driven Architecture Pattern

```
┌─────────────────────────────────────────────────┐
│ COMMAND (User Action)                          │
│ - Create/Update/Delete Task                    │
│ - Set Reminder                                 │
│ - Mark Complete                                │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ DATABASE OPERATION (Atomic)                    │
│ - Task persisted                               │
│ - State committed                              │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ EVENT PUBLISHED (Best-effort async)            │
│ - event_id (UUID)                              │
│ - event_type (string)                          │
│ - user_id (for isolation)                      │
│ - aggregate_id (task_id)                       │
│ - timestamp (ISO-8601)                         │
│ - data (JSON payload)                          │
│ - correlation_id (tracing)                     │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ EVENT CONSUMED (Multiple subscribers)          │
│ - WebSocket notifier                           │
│ - Scheduler (for recurring/reminder checks)    │
│ - Audit logger                                 │
│ - Analytics (future)                           │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ CLIENT NOTIFICATION                            │
│ - WebSocket message sent to connected clients  │
│ - Auto-reconnect if disconnected               │
│ - Fallback to polling if WebSocket unavailable │
└─────────────────────────────────────────────────┘
```

---

## Data Flow Between Services

### Task Creation Data Flow

```
REST Request
├─ Headers: Authorization: Bearer {JWT}
├─ Body: {title, description, due_date?, recurrence_rule?}
└─ Response: {id, user_id, title, ...}

Event Payload
├─ event_id: UUID
├─ event_type: "task.created"
├─ user_id: {from JWT}
├─ aggregate_id: {task_id}
├─ timestamp: ISO-8601
├─ data: {title, description, due_date, recurrence_rule}
└─ correlation_id: UUID (trace across systems)

WebSocket Message
├─ type: "task.created"
├─ data: {id, title, description, ...}
├─ timestamp: ISO-8601
└─ correlation_id: UUID
```

### Recurring Task Spawn Data Flow

```
Scheduler Internal
├─ Query: tasks WHERE next_occurrence <= NOW()
├─ For each task:
│  ├─ Calculate next_occurrence (using RRULE + timezone)
│  ├─ Create new Task instance
│  └─ Publish event

Event Payload
├─ event_id: UUID
├─ event_type: "task.created" (from recurrence)
├─ user_id: {original task user}
├─ aggregate_id: {new task_id}
├─ timestamp: ISO-8601
├─ data: {title (from parent), description (from parent), ...}
└─ correlation_id: {same as original if traceable}

Resulting in same WebSocket notification as manual creation
```

### Reminder Notification Data Flow

```
Scheduler Internal
├─ Query: reminders WHERE remind_at <= NOW() AND notified = false
├─ For each reminder:
│  ├─ Update reminder SET notified = true
│  └─ Publish event

Event Payload
├─ event_id: UUID
├─ event_type: "reminder.triggered"
├─ user_id: {task owner}
├─ aggregate_id: {reminder_id}
├─ timestamp: ISO-8601
├─ data: {task_id, remind_at, reminder_message}
└─ correlation_id: UUID

WebSocket Message
├─ type: "reminder"
├─ data: {task_id, task_title, reminder_message}
├─ timestamp: ISO-8601
└─ correlation_id: UUID (links to scheduler event)
```

---

## Deployment Architectures

### Option 1: Local Development (Minikube + Dapr + Redpanda)

```
┌──────────────────────────────────────────────────┐
│          Minikube Cluster (4GB RAM)              │
├──────────────────────────────────────────────────┤
│                                                  │
│  Namespace: taskflow                             │
│  ┌────────────────────────────────────────────┐  │
│  │ Frontend Pod                               │  │
│  │ - Next.js standalone build                 │  │
│  │ - Port 3000                                │  │
│  │ - 1 replica                                │  │
│  └────────────────────────────────────────────┘  │
│           │ HTTP                                 │
│  ┌────────▼────────────────────────────────────┐  │
│  │ Backend Pod (with Dapr sidecar)            │  │
│  │ - FastAPI uvicorn                          │  │
│  │ - Port 8000                                │  │
│  │ - Dapr sidecar port 3500 (pub/sub)        │  │
│  │ - 1 replica (scaling via kubectl scale)    │  │
│  └────────────────────────────────────────────┘  │
│           │ Dapr pub/sub                         │
│  ┌────────▼────────────────────────────────────┐  │
│  │ Redpanda Pod                               │  │
│  │ - Kafka broker                             │  │
│  │ - Port 9092                                │  │
│  │ - 1 replica                                │  │
│  └────────────────────────────────────────────┘  │
│           │                                      │
│  ┌────────▼────────────────────────────────────┐  │
│  │ Redis Pod (Dapr state store)               │  │
│  │ - Port 6379                                │  │
│  │ - 1 replica                                │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  External:                                       │
│  - Neon PostgreSQL (cloud URL)                   │
│  - Docker Desktop (container runtime)            │
│                                                  │
└──────────────────────────────────────────────────┘

Services:
- taskflow-frontend: ClusterIP, port 3000
- taskflow-backend: ClusterIP, port 8000
- redpanda: ClusterIP, port 9092
- redis: ClusterIP, port 6379
```

### Option 2: Cloud Simple (Vercel + Render + Redpanda Cloud)

```
┌──────────────────────────────────────────────────┐
│        Cloud Deployment (No Kubernetes)          │
├──────────────────────────────────────────────────┤
│                                                  │
│  Vercel Edge Network                             │
│  ┌────────────────────────────────────────────┐  │
│  │ Frontend Deployment                        │  │
│  │ - Next.js with Vercel                      │  │
│  │ - CDN-cached static assets                 │  │
│  │ - Automatic scaling (unlimited)            │  │
│  │ - Environment: NEXT_PUBLIC_API_URL         │  │
│  └────────────────────────────────────────────┘  │
│           │ HTTPS                                │
│  ┌────────▼────────────────────────────────────┐  │
│  │ Render.com Backend                         │  │
│  │ - Docker container deployment              │  │
│  │ - uvicorn on port 8000                     │  │
│  │ - 1 active instance (FREE tier)            │  │
│  │ - Auto-sleep after 15 min inactivity       │  │
│  │ - Environment:                             │  │
│  │   - DATABASE_URL (Neon)                    │  │
│  │   - KAFKA_BOOTSTRAP_SERVERS                │  │
│  │   - KAFKA_SASL_* (credentials)             │  │
│  │   - USE_DAPR=false                         │  │
│  └────────────────────────────────────────────┘  │
│           │ Direct Kafka client                  │
│           │ (no Dapr)                            │
│  ┌────────▼────────────────────────────────────┐  │
│  │ Redpanda Cloud Serverless                  │  │
│  │ - Managed Kafka                            │  │
│  │ - 10GB/month FREE tier                     │  │
│  │ - SASL/SSL authentication                  │  │
│  │ - Broker URL from Redpanda console         │  │
│  └────────────────────────────────────────────┘  │
│           │                                      │
│  ┌────────▼────────────────────────────────────┐  │
│  │ Neon PostgreSQL                            │  │
│  │ - Cloud PostgreSQL                         │  │
│  │ - FREE tier (5 GB storage)                 │  │
│  │ - Connection pool (handles Render timeout) │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  No Dapr (simpler but less cloud-native)        │
│  Backend uses aiokafka directly                 │
│                                                  │
└──────────────────────────────────────────────────┘

Cost: $0 (all free tiers)
Limitations:
- Single backend instance
- Render spins down after inactivity (cold start)
- No Dapr service mesh
- Simpler architecture
```

### Option 3: Cloud Kubernetes (Civo/Linode + Dapr + Redpanda Cloud)

```
┌──────────────────────────────────────────────────┐
│    Kubernetes Cluster (Civo or Linode)           │
│    ($250 credit Civo OR $100 Linode)             │
├──────────────────────────────────────────────────┤
│                                                  │
│  Namespace: taskflow                             │
│  ┌────────────────────────────────────────────┐  │
│  │ Ingress (LoadBalancer)                     │  │
│  │ - Routes HTTP traffic to services          │  │
│  │ - TLS termination (Let's Encrypt)          │  │
│  │ - Public IP address                        │  │
│  └────────────────────────────────────────────┘  │
│           │ HTTP/HTTPS                           │
│  ┌────────▼────────────────────────────────────┐  │
│  │ Frontend Service + Deployment              │  │
│  │ - 1-3 replicas (Horizontal Pod Autoscaler) │  │
│  │ - NextJs standalone                        │  │
│  │ - Port 3000                                │  │
│  └────────────────────────────────────────────┘  │
│           │ Service DNS name                     │
│  ┌────────▼────────────────────────────────────┐  │
│  │ Backend Service + Deployment (Dapr)        │  │
│  │ - 1-3 replicas (Horizontal Pod Autoscaler) │  │
│  │ - FastAPI uvicorn                          │  │
│  │ - Port 8000                                │  │
│  │ - Dapr sidecar injection enabled           │  │
│  │   • dapr.io/enabled: "true"                │  │
│  │   • dapr.io/app-id: "backend"              │  │
│  │   • dapr.io/app-port: "8000"               │  │
│  │ - Metrics for autoscaling                  │  │
│  └────────────────────────────────────────────┘  │
│           │ Dapr pub/sub                         │
│  ┌────────▼────────────────────────────────────┐  │
│  │ Scheduler Service + Deployment             │  │
│  │ - 1 replica (no scaling)                   │  │
│  │ - APScheduler                              │  │
│  │ - Prevents duplicate recurrence triggers   │  │
│  └────────────────────────────────────────────┘  │
│           │ Dapr pub/sub                         │
│  ┌────────▼────────────────────────────────────┐  │
│  │ Redis Pod (Dapr state store)               │  │
│  │ - Port 6379                                │  │
│  │ - 1 replica with persistence               │  │
│  │ - Dapr references this for state mgmt      │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  ConfigMaps:                                     │
│  - app-config (non-secret env vars)             │
│                                                  │
│  Secrets:                                        │
│  - taskflow-secrets:                            │
│    • DATABASE_URL (Neon PostgreSQL)             │
│    • KAFKA_BROKERS (Redpanda Cloud URL)         │
│    • KAFKA_SASL_USERNAME                        │
│    • KAFKA_SASL_PASSWORD                        │
│    • BETTER_AUTH_SECRET                         │
│    • OPENAI_API_KEY                             │
│    • USE_DAPR=true                              │
│                                                  │
│  External:                                       │
│  - Neon PostgreSQL (cloud database)             │
│  - Redpanda Cloud Serverless (Kafka)            │
│                                                  │
└──────────────────────────────────────────────────┘

Cost: $0 for 2-3 months (free tier credits)
        Then $0 if scaled appropriately

Features:
- Full cloud-native architecture
- Dapr sidecar on all services
- Horizontal scaling built-in
- Production-ready (demonstrates K8s skills)
```

---

## Deployment Comparison Summary

| Aspect | Local (Minikube) | Cloud Simple (Vercel/Render) | Cloud K8s (Civo) |
|--------|------------------|------------------------------|------------------|
| **Frontend** | Minikube | Vercel | K8s Ingress |
| **Backend** | K8s Pod | Render (Docker) | K8s Pod + Dapr |
| **Kafka** | Redpanda Docker | Redpanda Cloud | Redpanda Cloud |
| **Database** | Neon PostgreSQL | Neon PostgreSQL | Neon PostgreSQL |
| **Cost** | $0 | $0 (FREE tier) | $0 (trial credits) |
| **Complexity** | Low (local) | Low (managed) | High (infrastructure) |
| **Dapr** | Yes (sidecar) | No (direct clients) | Yes (sidecar) |
| **Scaling** | Manual (kubectl) | Render handles | Auto (HPA) |
| **Development** | Recommended | Demo/quick test | Portfolio showcase |
| **Production** | Not suitable | Suitable (single instance) | Suitable (multi-replica) |
| **Cold Start** | ~30s | ~60s Render | ~20s K8s |

---

## Key Architectural Decisions

1. **Kafka Partitioning by user_id**: Ensures events for single user processed in order; enables per-user scaling
2. **Dapr Optional for Cloud**: Simplifies local development; cloud deployments work without it (lower cognitive load)
3. **WebSocket Auto-Reconnect**: Frontend handles interruptions transparently; fallback to polling if needed
4. **Event Publishing Post-DB**: Database operation atomic first; event publishing best-effort async
5. **Scheduler as Single Replica**: Prevents duplicate recurrence triggers; acceptable for 1000+ users
6. **Graceful Degradation**: System continues functioning if Kafka unavailable (DB queue fallback)
7. **User Isolation at Multiple Levels**: JWT validation, Kafka partition filtering, WebSocket subscription filtering
