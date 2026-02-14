<!--
  SYNC IMPACT REPORT - Phase V Constitution Amendment
  Version: 3.1.0 → 4.0.0 (MAJOR bump: Event-Driven Architecture replaces REST-centric model)
  Date: 2026-02-14

  Previous Version (3.1.0) Changes:
  - Phases II-IV: REST API, stateless backend, Kubernetes/Docker/Helm infrastructure

  Current Version (4.0.0) Changes - MAJOR SHIFT:
  - ADDED Principle XVIII: Event-Driven Architecture (Kafka/Redpanda)
  - ADDED Principle XIX: Dapr Service Mesh Integration (local/K8s)
  - ADDED Principle XX: Loose Coupling via Event Streaming
  - ADDED Principle XXI: Observability & Event Traceability
  - ADDED Principle XXII: Cost-Optimized Free-Tier Deployment
  - ADDED Principle XXIII: Recurring Tasks with Scheduling
  - ADDED Principle XXIV: Real-Time WebSocket Communication
  - Extended Technology Stack: Kafka/Redpanda, Dapr, WebSockets
  - Extended Architectural Constraints: Event sourcing, async processing, graceful degradation
  - Added Event-Driven Coding Standards: Event handlers, retry logic, idempotent operations
  - Added Testing Requirements: Event flow integration tests, replay capability, load testing
  - Extended Deployment: Docker Compose for local Kafka, cloud Redpanda Serverless
  - New Deployment Options: Option A (Vercel/Render, no K8s), Option B (Civo K8s with Dapr)

  Templates Requiring Updates:
  - .specify/templates/plan-template.md: Add event architecture section (⚠ pending)
  - .specify/templates/spec-template.md: Add event-driven requirements section (⚠ pending)
  - .specify/templates/tasks-template.md: Add "Event Handler" and "Kafka Integration" task categories (⚠ pending)
  - README.md: Update to reference Phase V features and deployment options (⚠ pending)

  Deferred Items: None
-->

# Full-Stack Todo Application Constitution - Phase V Extension

<!-- Phase II: Production-Ready Multi-User Web Application -->
<!-- Phase III: AI-Powered Conversational Interface with MCP Integration -->
<!-- Phase IV: Local Kubernetes Deployment on Minikube -->
<!-- Phase V: Distributed Cloud-Native AI Todo System with Event-Driven Architecture -->

## Core Principles

### I. Security First (NON-NEGOTIABLE)
- **Authentication Required**: All task operations and chat interactions require valid JWT authentication
- **User Isolation Enforced**: Users can only access their own data and conversations; backend validates user_id from JWT matches path user_id on every request
- **Zero Trust**: All inputs validated at API boundary (frontend AND backend); SQL injection prevented via ORM; XSS prevented via React escaping
- **Secrets Management**: All secrets in environment variables (.env files for dev); K8s Secrets for deployment; Never hardcoded; .gitignore excludes all .env files
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
- **Connection Management**: Neon Serverless PostgreSQL; Connection pooling enabled; pool_pre_ping=True for health checks; Connection string from environment variable (or K8s Secret in deployment)

### VI. Authentication & JWT Flow (Better Auth)
- **Better Auth Library**: JWT plugin enabled; Token expiration: 7 days (configurable); Secure password hashing (bcrypt); Email validation
- **JWT Token Flow**: Better Auth issues JWT on login → Stored in httpOnly cookies → Sent in Authorization: Bearer <token> header → Backend verifies JWT signature with shared secret → Extract user_id from token payload (sub claim) → Validate user_id in URL matches token user_id
- **Shared Secret**: BETTER_AUTH_SECRET environment variable (K8s Secret in deployment); Same secret in frontend and backend; Minimum 32 characters; Random, cryptographically secure; Never hardcoded

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

### XIII. Container-First Design (Phase IV)
- **All Components Containerized**: Frontend and Backend MUST run in Docker containers; No bare-metal dependencies in deployment
- **Multi-Stage Builds Required**: Dockerfiles MUST use multi-stage builds for optimization; Build stage separate from runtime stage
- **Minimal Base Images**: Use alpine or slim variants (node:20-alpine, python:3.13-slim); No full OS images
- **No Hardcoded Configuration**: All configuration externalized via environment variables; Containers are environment-agnostic
- **Stateless Containers**: No local file storage; All persistent data in external Neon database; Containers can be killed and recreated without data loss

### XIV. Kubernetes-Native Patterns (Phase IV)
- **Deployments Over Pods**: Always use Deployment resources (not standalone Pods); Enables rolling updates and replica management
- **Services for Networking**: Frontend and Backend exposed via K8s Services; ClusterIP for internal, NodePort/LoadBalancer for external access
- **ConfigMaps for Non-Secret Config**: API URLs, feature flags, non-sensitive settings in ConfigMaps
- **Secrets for Sensitive Data**: DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY MUST be K8s Secrets; Never in ConfigMaps or Helm values
- **Health Checks Required**: Liveness and Readiness probes defined for all containers; Prevents traffic to unhealthy pods
- **Resource Management**: CPU/Memory requests and limits MUST be defined; Prevents resource starvation and enables proper scheduling

### XV. Infrastructure as Code (Phase IV)
- **Declarative Configuration**: All K8s resources defined in version-controlled files; No imperative kubectl create/run commands in production workflow
- **Reproducible Deployments**: Same manifests produce identical deployments; Environment differences handled via values files
- **GitOps Ready**: Infrastructure changes go through same PR review as application code; Audit trail for all deployment changes
- **Idempotent Operations**: helm upgrade --install pattern; Applying same config twice has no side effects

### XVI. Helm Standards (Phase IV)
- **Helm as Package Manager**: All K8s resources defined in Helm charts; No raw kubectl apply on individual YAML files
- **Values-Driven Configuration**: All customizable settings in values.yaml; Environment overrides in values-dev.yaml, values-prod.yaml
- **Templated Manifests**: Use Helm templating for DRY configurations; {{ .Values.* }} for all configurable fields
- **Chart Structure**: Follow standard Helm chart layout (Chart.yaml, values.yaml, templates/)
- **Dependency Management**: External charts referenced in Chart.yaml dependencies; Version-pinned dependencies

### XVII. Command Automation (Phase IV)
- **AI-Executed Infrastructure**: Claude Code executes ALL infrastructure commands (docker build, helm install, kubectl, minikube)
- **No Manual Command Entry**: User MUST NOT need to copy-paste commands; Claude Code runs them directly
- **Scripted Operations**: Common operations wrapped in reusable patterns for consistent execution
- **Error Handling**: Claude Code handles command failures, diagnoses issues, and retries or escalates appropriately
- **Progress Reporting**: Clear feedback to user on command status (building, deploying, verifying)
- **Idempotent Execution**: Commands designed to be safe to re-run without side effects

### XVIII. Event-Driven Architecture (Phase V) - NEW
- **All State Changes Emit Events**: Task created, updated, completed, deleted, due date changed MUST emit events to Kafka
- **Event Schema**: Every event contains: `event_id` (UUID), `event_type` (string), `user_id` (required for isolation), `timestamp` (ISO-8601), `aggregate_id` (task_id or conversation_id), `data` (JSON payload), `version` (for replay)
- **Exactly-Once Semantics**: Event publishing idempotent; duplicate events handled gracefully; event_id deduplication prevents double-processing
- **Event Topics**: Separate Kafka topics per aggregate: `tasks.events`, `conversations.events`, `users.events`
- **Async Processing**: Event handlers subscribe to topics and process independently; no blocking HTTP calls for event handling
- **Event Sourcing Capability**: Complete audit trail; ability to replay events to rebuild state; event log is system of record

### XIX. Dapr Service Mesh Integration (Phase V) - NEW
- **Local Development Only**: Dapr sidecar pattern for task orchestration, pub/sub, state management, secrets (Minikube/Docker Compose)
- **Cloud Graceful Degradation**: Cloud deployments (Vercel/Render) bypass Dapr; direct Kafka clients and HTTP calls instead
- **Pub/Sub Abstraction**: Dapr provides pub/sub abstraction for Kafka; allows easy swapping of event streaming backends
- **State Management**: Dapr state store for transient task processing state (not persistent data)
- **Secrets Store**: Dapr secrets store integration for local Kubernetes (K8s Secrets are native)
- **Service Invocation**: Dapr enables service-to-service calls with automatic retries and circuit breakers (local only)

### XX. Loose Coupling via Event Streaming (Phase V) - NEW
- **No Direct Service-to-Service Calls**: Backend services do NOT call each other directly
- **Event-Based Communication**: Services communicate via published/subscribed events on Kafka
- **Independent Scaling**: Each service scales independently based on event queue depth
- **Topic Subscriptions**: Consumer groups ensure each service processes all relevant events exactly once
- **Dead Letter Queues**: Failed event processing routes to DLQ for manual retry/analysis

### XXI. Observability & Event Traceability (Phase V) - NEW
- **Correlation IDs**: All events and HTTP requests include X-Correlation-ID header for tracing
- **Structured Logging**: All log entries include: timestamp, correlation_id, user_id, service_name, event_type, status (success/failure)
- **Event Audit Trail**: All events immutable; stored with full context for compliance and debugging
- **Health Checks Enhanced**: Include event queue depth, lag, and processing errors
- **Metrics**: Track event throughput, latency, failure rates, consumer lag
- **Tracing**: Optional OpenTelemetry integration for distributed tracing across services

### XXII. Cost-Optimized Free-Tier Deployment (Phase V) - NEW
- **100% Free Services**: All cloud deployment uses only free-tier or free-trial services; no paid tiers
- **Deployment Option A - Simple (Vercel/Render)**: Frontend on Vercel, Backend on Render, Redpanda Cloud Serverless (10GB/month free)
- **Deployment Option B - Kubernetes (Civo/Linode)**: Free K8s credits ($250 Civo or $100 Linode), Neon PostgreSQL free tier, Redpanda Cloud free tier
- **Local Development**: Docker Compose with Redpanda container (no external services except Neon for data)
- **Cost Awareness**: All code must account for resource limits; graceful degradation when approaching quotas

### XXIII. Recurring Tasks with Scheduling (Phase V) - NEW
- **Recurrence Support**: Tasks support recurrence patterns: none, daily, weekly, monthly
- **Scheduler Service**: Background service processes recurrence; creates new task instances on schedule
- **Event-Driven Scheduling**: Recurrence trigger events published to `tasks.scheduling` topic; scheduler subscribes and acts
- **Timezone Support**: User timezone stored; recurrence calculations respect user local time
- **Soft Recurrence**: Completed recurring tasks spawn next instance; original stays in history

### XXIV. Real-Time Updates via WebSocket (Phase V) - NEW
- **WebSocket Endpoint**: `/ws/user/{user_id}/tasks` for real-time task updates
- **JWT Validation on Connect**: WebSocket handshake validates JWT; connection rejected if invalid
- **Event Streaming to Clients**: When task event published to Kafka, immediately broadcast to connected WebSocket clients
- **Auto-Reconnect Logic**: Frontend WebSocket with exponential backoff on disconnect; reconnect attempts up to 5 times
- **Message Format**: `{"type": "task.created|updated|deleted|completed", "data": {...}, "timestamp": "..."}`
- **Fallback to Polling**: If WebSocket unavailable, frontend falls back to HTTP polling (30-second intervals)

## Technology Stack

### Frontend Stack
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth (client)
- **State**: React hooks (useState, useEffect, useCallback, useMemo)
- **HTTP Client**: Fetch API (built-in)
- **WebSocket Client**: Browser WebSocket API with reconnection logic
- **Chat UI Kit**: OpenAI ChatKit (TypeScript)
- **Container**: Docker (node:20-alpine base)
- **Deployment**: Kubernetes (Minikube local), Vercel (cloud Option A)

### Backend Stack
- **Framework**: FastAPI (async/await)
- **Language**: Python 3.13+ (type hints)
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless - external to K8s)
- **Authentication**: JWT verification (shared secret with Better Auth)
- **Validation**: Pydantic models
- **AI Agent Framework**: OpenAI Agents SDK (Python)
- **MCP Protocol**: Model Context Protocol (server-side MCP implementation)
- **LLM**: OpenAI API (gpt-4o or latest reasoning model)
- **Event Streaming**: Kafka / Redpanda (local Docker, cloud Serverless)
- **Kafka Client**: aiokafka (async Python Kafka client)
- **WebSocket Support**: websockets library or Starlette WebSocket
- **Async Task Processing**: APScheduler (for scheduling recurrence)
- **Dapr Integration**: dapr-sdk (local/K8s only)
- **Container**: Docker (python:3.13-slim base)
- **Deployment**: Kubernetes (Minikube local), Render.com (cloud Option A), Civo K8s (cloud Option B)

### Event Streaming Stack
- **Local**: Docker Compose with Redpanda container (docker.io/redpandadata/redpanda)
- **Cloud Option A**: Redpanda Cloud Serverless (free tier, 10GB/month)
- **Cloud Option B**: Redpanda Cloud (deployed in K8s via Helm, or external managed instance)
- **Kafka CLI**: kcat/kafkacat for debugging

### Infrastructure Stack (Phase V)
- **Container Runtime**: Docker Desktop
- **Local Kubernetes**: Minikube (with Dapr installed)
- **Service Mesh (Local)**: Dapr v1.12+
- **Package Manager**: Helm 3
- **Local Event Streaming**: Docker Compose (Redpanda)
- **CLI Tools**: kubectl, docker, helm, minikube, dapr
- **Orchestration**: Kubernetes (Minikube) or managed K8s (Civo/Linode)

### Development Tools
- **Package Managers**: npm (frontend), pip/uv (backend)
- **Environment Files**: .env.local (frontend dev), .env (backend dev)
- **Version Control**: Git + GitHub
- **Code Organization**: Separate frontend/ and backend/ folders
- **Infrastructure Code**: k8s/, helm/, dapr/ folders at repository root
- **Event Debugging**: Redpanda Console or kcat CLI

## Architectural Constraints (Phase V)

### Event Streaming Requirements
- **Kafka Topic Strategy**: Topics per aggregate type (tasks, conversations, users); events immutable once published
- **Consumer Groups**: Each service instance in a consumer group; automatic load balancing and failover
- **Retention Policy**: Events retained for minimum 7 days (configurable); allows late-joining consumers
- **Partitioning**: Topics partitioned by user_id to ensure ordering per user
- **Schema Registry**: Optional (Redpanda has schema validation); events validated against schema

### Dapr Component Integration (Local/K8s)
- **Pub/Sub Component**: Dapr references Kafka; services use Dapr APIs (not direct Kafka clients)
- **State Store**: Dapr state stores task processing state (ephemeral, not persistent)
- **Secrets**: K8s Secrets in Kubernetes; local secrets file in Docker Compose
- **Service Invocation**: Dapr handles inter-service retries and timeouts
- **Configuration**: Dapr components defined in YAML files in dapr/ folder

### WebSocket Constraints
- **Connection Limits**: Backend supports 100+ concurrent WebSocket connections per instance
- **Message Rate**: Max 10 messages/second per connection (prevent spam)
- **Timeout**: 5-minute inactivity timeout; connection closed and client reconnects
- **State Minimalism**: WebSocket handlers MUST be stateless; subscriptions managed via Kafka consumer groups

### Scheduling Constraints
- **Scheduler Service**: Dedicated service for processing recurring tasks; runs as 1 replica (prevents duplicate scheduling)
- **Schedule Precision**: Recurrence tasks processed within 5 minutes of scheduled time (not strict)
- **Timezone Handling**: User's local timezone stored; scheduler converts to UTC internally

### Container Requirements (Unchanged)
- **Frontend Container**: Node.js 20 alpine, standalone Next.js build, <200MB image size
- **Backend Container**: Python 3.13 slim, uvicorn ASGI server, <300MB image size, includes event handlers
- **No Local Dependencies**: Containers MUST NOT depend on host machine binaries or paths
- **Port Standardization**: Frontend: 3000 (internal), Backend: 8000 (internal), Kafka: 9092 (internal)

### Kubernetes Design (Unchanged)
- **Namespace Isolation**: All TaskFlow resources in dedicated namespace (taskflow)
- **Label Consistency**: All resources labeled with `app: taskflow`, `component: frontend|backend|scheduler`
- **Selector Alignment**: Deployment selectors MUST match Pod template labels
- **Service Discovery**: Services accessed via DNS names (taskflow-backend:8000), not IP addresses

### Resource Boundaries (Updated for Event Processing)
- **Frontend Deployment**: 1-3 replicas, 128Mi-256Mi memory, 100m-250m CPU
- **Backend Deployment**: 1-3 replicas, 512Mi-1Gi memory, 500m-1000m CPU (event processing)
- **Scheduler Deployment**: 1 replica (no scaling), 256Mi memory, 250m CPU
- **Event Handler Pods**: 1-2 replicas, 256Mi-512Mi memory, 250m-500m CPU

### External Dependencies (Updated)
- **Database**: Neon PostgreSQL remains external; accessed via DATABASE_URL secret
- **OpenAI API**: Accessed via OPENAI_API_KEY secret; no local LLM
- **Event Streaming**: Kafka/Redpanda (external SaaS for cloud, containerized for local)
- **No In-Cluster Database or Kafka**: Both remain external

## Coding Standards (Phase V Extensions)

### Event Handler Standards
```python
# REQUIRED: Type hints for all event handlers
from pydantic import BaseModel
from typing import Callable
from datetime import datetime

class TaskCreatedEvent(BaseModel):
    event_id: str
    event_type: str = "task.created"
    user_id: str
    aggregate_id: str  # task_id
    timestamp: datetime
    data: dict

async def handle_task_created(event: TaskCreatedEvent) -> None:
    """Process task created events."""
    # REQUIRED: User isolation check
    task = await db.get_task_by_id(event.aggregate_id, event.user_id)
    if not task:
        raise ValueError(f"Task {event.aggregate_id} not found for user {event.user_id}")

    # REQUIRED: Idempotent processing (check if already processed)
    if await cache.get(f"processed:{event.event_id}"):
        return  # Already processed, skip

    # REQUIRED: Error handling with retries
    try:
        await process_task_event(task, event)
        await cache.set(f"processed:{event.event_id}", "1", ex=86400)
    except Exception as e:
        # REQUIRED: Log and re-raise (framework handles retry)
        logger.error(f"Error processing {event.event_type}: {e}", extra={"event_id": event.event_id})
        raise

# REQUIRED: Register handler with consumer group
@app.on_event("startup")
async def subscribe_to_events():
    await kafka_consumer.subscribe(
        topic="tasks.events",
        group_id="task-processor",
        callback=handle_task_created
    )
```

**Rules**:
- MUST include correlation_id in all log entries
- MUST validate user_id before processing events
- MUST implement idempotency (event_id deduplication)
- MUST handle all exceptions and log comprehensively
- MUST use Pydantic models for event validation
- MUST retry on transient failures (exponential backoff)
- MUST be stateless (no in-memory event buffering)

### WebSocket Handler Standards
```python
from fastapi import WebSocket
from jose import JWTError

@app.websocket("/ws/user/{user_id}/tasks")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    # REQUIRED: JWT validation on connect
    token = websocket.query_params.get("token")
    try:
        payload = verify_jwt_token(token)
        if payload.get("sub") != user_id:
            await websocket.close(code=4003, reason="Unauthorized")
            return
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()

    # REQUIRED: Subscribe to user-specific Kafka topic
    consumer = await create_kafka_consumer(
        topic=f"user.{user_id}.tasks",
        group_id=f"ws-{user_id}"
    )

    try:
        async for event in consumer:
            # REQUIRED: Send to client with structured format
            await websocket.send_json({
                "type": event.event_type,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            })
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        await websocket.close()
```

**Rules**:
- MUST validate JWT on WebSocket connect
- MUST isolate subscriptions by user_id
- MUST handle client disconnects gracefully
- MUST not buffer messages in memory (Kafka is buffer)
- MUST close connection on auth failure

### Dockerfile Standards (Unchanged from Phase IV)
- Multi-stage builds required
- Non-root user mandatory
- No hardcoded secrets
- Specific version tags only

### Event Publishing Standards
```python
# REQUIRED: All task operations publish events
async def create_task(user_id: str, task_data: TaskCreate) -> Task:
    # 1. Create in database first (atomic operation)
    task = await db.create_task(user_id=user_id, data=task_data)

    # 2. Publish event (async, best-effort)
    event = TaskCreatedEvent(
        event_id=str(uuid.uuid4()),
        event_type="task.created",
        user_id=user_id,
        aggregate_id=task.id,
        timestamp=datetime.utcnow(),
        data={
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date.isoformat() if task.due_date else None
        }
    )

    try:
        await kafka_producer.send(
            topic="tasks.events",
            value=event.model_dump_json(),
            key=user_id  # Partition by user
        )
    except Exception as e:
        # REQUIRED: Log but don't fail (event queue might be temporarily unavailable)
        logger.warning(f"Failed to publish task.created event: {e}")

    return task
```

**Rules**:
- MUST publish events after database operation succeeds
- MUST include all event metadata (event_id, timestamp, user_id)
- MUST partition by user_id (ensures ordering per user)
- MUST handle publish failures gracefully (log, don't break flow)

## Event-Driven Coding Standards (Phase V)

### Retry Logic with Exponential Backoff
```python
import asyncio
from typing import Callable

async def with_retry(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
):
    """Execute function with exponential backoff retry."""
    attempt = 0
    while attempt < max_attempts:
        try:
            return await func()
        except Exception as e:
            attempt += 1
            if attempt >= max_attempts:
                raise

            delay = min(base_delay * (2 ** attempt), max_delay)
            logger.warning(f"Retry attempt {attempt}, waiting {delay}s: {e}")
            await asyncio.sleep(delay)
```

### Graceful Degradation When Kafka Unavailable
```python
async def publish_event_with_fallback(event: Event) -> None:
    """Publish event, fall back to database queue if Kafka unavailable."""
    try:
        await kafka_producer.send(
            topic=event.topic,
            value=event.model_dump_json(),
            key=str(event.user_id)
        )
    except Exception as e:
        logger.warning(f"Kafka unavailable, storing in database queue: {e}")
        # REQUIRED: Store in database as fallback
        await db.save_event_to_queue(event)
```

## Security Rules (Phase V)

### Event Streaming Security
- **User Isolation in Events**: All events MUST include user_id; consumers filter by user_id
- **Event Encryption**: Kafka SASL/SSL encryption for cloud (Redpanda Cloud enforces this)
- **Topic Access Control**: ACLs restrict which services can publish/consume which topics
- **Correlation ID in Logs**: Enables audit trail linking events to HTTP requests

### WebSocket Security
- **JWT Validation**: All WebSocket connections require valid JWT token in query string
- **HTTPS/WSS Only**: WebSocket connections MUST use WSS (secure WebSocket) in production
- **Rate Limiting**: Max 10 messages/second per connection to prevent flooding
- **CORS for WebSocket**: Origin validation same as HTTP CORS rules

### Secrets for Event Streaming
- **Kafka Credentials**: KAFKA_BROKERS, KAFKA_USERNAME, KAFKA_PASSWORD in K8s Secrets
- **Dapr Secrets**: Stored in Dapr secrets store (local) or K8s Secrets (cloud)
- **No Secrets in Events**: Events never contain passwords, API keys, or PII

## Performance Expectations (Phase V)

### Event Processing
- **Event Throughput**: Handle 1000+ events/second per backend instance
- **Event Latency**: Events published → processed within 500ms (p99)
- **Consumer Lag**: Lag should stay <1000 messages for healthy system
- **Kafka Retention**: 7-day retention; no message loss during 7 days

### WebSocket Performance
- **Connection Latency**: WebSocket connection established within 200ms
- **Message Delivery**: Events pushed to connected clients within 100ms of publishing
- **Concurrent Connections**: Support 100+ concurrent WebSocket connections per backend instance
- **Reconnection Time**: Auto-reconnect completes within 2-5 seconds

### Scheduler Performance
- **Recurrence Accuracy**: Recurring tasks spawn within 5 minutes of scheduled time
- **Throughput**: Scheduler processes 100+ recurrence triggers per minute
- **No Memory Leaks**: Scheduler runs continuously without memory growth

### Resource Efficiency (Updated)
- **Backend Event Processing**: <512MB memory per instance (baseline), scales with queue depth
- **Scheduler Service**: <256MB memory (constant)
- **Event Queue Disk**: Kafka stores events on disk; doesn't consume pod memory
- **CPU for Event Handling**: <500m CPU at 1000 events/sec

## Testing Requirements (Phase V)

### Event Handler Tests
- [ ] Event handlers validate user_id before processing
- [ ] Event handlers are idempotent (duplicate events handled correctly)
- [ ] Failed event processing routes to DLQ
- [ ] Handlers implement retry logic with backoff
- [ ] Correlation IDs propagate through event chain

### Event Integration Tests
- [ ] Task creation → event published → listener receives event
- [ ] Task update → event published → WebSocket clients notified
- [ ] WebSocket connection → receives historical and new events
- [ ] WebSocket reconnection → resumes without data loss
- [ ] Kafka unavailable → system gracefully falls back

### WebSocket Tests
- [ ] WebSocket rejects connections without valid JWT
- [ ] WebSocket sends events to connected clients
- [ ] WebSocket handles client disconnect gracefully
- [ ] WebSocket rate limiting prevents spam (>10 msgs/sec rejected)
- [ ] Frontend reconnect logic works on network interruption

### End-to-End Event Flow Tests
- [ ] User creates task via REST API → event published → WebSocket clients see update
- [ ] Recurring task scheduled → new task spawned on schedule → event emitted
- [ ] Multiple users' events isolated (user A doesn't see user B's task events)
- [ ] Event replay: delete Kafka topic → republish from database queue

### Load Testing
- [ ] Backend handles 1000 events/second without lag
- [ ] Scheduler spawns 100+ recurring tasks per minute
- [ ] WebSocket server maintains 100+ concurrent connections with <100ms latency
- [ ] No memory leaks after 1 hour of event processing

## Non-Negotiables (Phase V)

### MUST Have
- All task operations publish events to Kafka
- All events include event_id, user_id, timestamp, aggregate_id
- Event handlers are idempotent
- Event handlers validate user_id
- Event handlers implement retry logic
- WebSocket handlers validate JWT
- WebSocket messages include type and timestamp
- Correlation IDs in all logs
- Graceful degradation when Kafka unavailable
- Events retain for 7+ days

### MUST NOT Have
- Hardcoded Kafka broker addresses
- Direct database queries in event handlers (use Pydantic models only)
- User data in WebSocket broadcasts (only event metadata)
- WebSocket connections without JWT validation
- Event handlers with state (must be stateless)
- Secrets in Kafka event payloads
- Event duplication without deduplication logic
- Blocking HTTP calls in async event handlers

## Deployment Standards (Phase V)

### Local Development with Docker Compose
```yaml
# docker-compose.yml
services:
  redpanda:
    image: redpandadata/redpanda:latest
    ports:
      - "9092:9092"
    environment:
      - REDPANDA_BROKERS=redpanda:9092

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - KAFKA_BROKERS=redpanda:9092
      - DAPR_HOST=dapr-sidecar
    depends_on:
      - redpanda

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Deployment Option A: Vercel + Render + Redpanda Serverless (No Kubernetes)
**Tech Stack**:
- Frontend: Vercel (FREE forever, unlimited)
- Backend: Render.com (FREE tier, 750 hrs/month)
- Database: Neon PostgreSQL (FREE tier)
- Event Streaming: Redpanda Cloud Serverless (FREE tier, 10GB/month)

**Architecture**:
- No Dapr (cloud services communicate via direct HTTP + Kafka clients)
- Backend runs as single instance on Render (scaling requires paid tier)
- Event handlers run within backend process (no separate scheduler)
- WebSocket via Render's native support

**Deployment Steps**:
1. Deploy frontend to Vercel from GitHub
2. Deploy backend to Render from GitHub
3. Create Redpanda Cloud Serverless cluster (free tier)
4. Set environment variables on Render: DATABASE_URL, KAFKA_BROKERS, KAFKA_CREDENTIALS

### Deployment Option B: Kubernetes with Dapr (Cloud or Local)
**Tech Stack**:
- Frontend: Deployed in K8s as Deployment + Service (on Civo/Linode)
- Backend: Deployed in K8s as Deployment + Service with Dapr sidecar
- Scheduler: Separate Deployment in K8s (Dapr-enabled)
- Database: Neon PostgreSQL (external)
- Event Streaming: Redpanda Cloud OR managed Kafka on K8s
- Service Mesh: Dapr sidecar on all services

**Architecture**:
- All services in taskflow namespace
- Dapr sidecar injected on backend and scheduler pods
- Pub/sub abstraction hides Kafka complexity
- Helm charts manage all K8s resources

**Deployment Steps**:
1. Create Kubernetes cluster (Civo: FREE $250 credit; Linode: FREE $100 credit)
2. Install Dapr on cluster: `dapr init -k`
3. Build and push container images to registry
4. Deploy via Helm: `helm install taskflow ./charts/taskflow`
5. Create K8s Secrets for DATABASE_URL, KAFKA credentials
6. Verify: `kubectl get pods -n taskflow`, `kubectl get services -n taskflow`

### Project Structure (Phase V)
```
project-root/
├── frontend/
│   ├── Dockerfile
│   ├── app/
│   │   └── dashboard/
│   │       └── page.tsx          # Real-time task list via WebSocket
│   └── lib/
│       └── websocket-client.ts   # WebSocket with auto-reconnect
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── routes/
│   │   ├── tasks.py              # REST endpoints
│   │   └── websocket.py          # WebSocket endpoints
│   ├── handlers/
│   │   ├── task_events.py        # Event handler for task events
│   │   ├── schedule_handler.py   # Recurrence scheduling
│   │   └── event_publisher.py    # Event publishing utilities
│   └── models.py                 # Add recurring_pattern to Task model
├── charts/
│   └── taskflow/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       └── templates/
│           ├── backend-deployment.yaml  # Dapr sidecar annotation
│           ├── scheduler-deployment.yaml
│           └── ...
├── dapr/
│   ├── components.yaml           # Pub/sub component definition
│   ├── state-store.yaml
│   └── secrets.yaml
├── docker-compose.yml            # Local dev with Redpanda
├── k8s-manifests.yaml            # Raw K8s (alternative to Helm)
├── K8S_SETUP.md                  # K8s deployment guide
├── DEPLOYMENT.md                 # OPTION A vs OPTION B guide
├── ARCHITECTURE.md               # Event flow diagrams
├── CLOUD_OPTIONS.md              # Free tier comparison
└── README.md                     # Phase V features
```

## Governance

### Constitution Authority
- This constitution supersedes all other practices and guidelines
- All code, specs, infrastructure, and implementations must comply with these principles
- Amendments require documentation and approval via /sp.constitution
- CLAUDE.md provides runtime development guidance and must align with this constitution

### Compliance Verification
- All PRs/reviews must verify: security, type safety, API standards, K8s best practices, event handler idempotency
- Event handler code must show user_id validation and retry logic
- WebSocket handlers must show JWT validation
- Infrastructure changes reviewed with same rigor as application code
- Complexity must be justified; simple solutions preferred
- Over-engineering is explicitly discouraged
- Event isolation must be tested with multiple users before deployment
- Kafka/Redpanda connectivity tested in all deployment options

### Development Philosophy
- **Spec-Driven Development (SDD)**: All features start with specifications
- **AI-Assisted Generation**: AI generates code from specs following this constitution
- **Human as Tool**: Invoke user for clarifications, architectural decisions, and ambiguous requirements
- **Smallest Viable Change**: No refactoring unrelated code; focused changes only
- **Infrastructure as Code**: K8s resources treated as first-class code artifacts
- **Event-First Design**: Think about events emitted before writing REST endpoints

### Version Control
- **Semantic Versioning**: MAJOR.MINOR.PATCH
  - MAJOR: Backward incompatible architecture shifts (e.g., REST → Event-Driven)
  - MINOR: New principle/section added or materially expanded guidance
  - PATCH: Clarifications, wording, typo fixes, non-semantic refinements
- **Amendment Log**: Each amendment updates LAST_AMENDED_DATE and documents changes in Sync Impact Report comment

**Version**: 4.0.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2026-02-14
