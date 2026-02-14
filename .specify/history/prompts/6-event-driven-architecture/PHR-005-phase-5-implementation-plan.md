---
id: "PHR-005"
date: 2026-02-14
stage: plan
title: "Phase 5 Event-Driven Implementation Plan"
status: completed
---

# Prompt History Record: Phase 5 Implementation Plan

## Metadata
- **ID**: PHR-005
- **Date**: 2026-02-14
- **Stage**: plan
- **Feature**: 6-event-driven-architecture
- **Title**: Phase 5: Distributed Cloud-Native Event-Driven Todo System - Implementation Plan

## Summary
User requested comprehensive implementation plan for Phase 5 organized into 12 phases with dependencies, optimized for FREE deployment. Plan covers infrastructure setup, database schema, event system foundation, features (recurring tasks, reminders, real-time), Kubernetes/Helm deployment, and three cloud options.

## Plan Structure

### Technical Context Established
- Language/Version: Python 3.13 (backend), TypeScript/Next.js 16 (frontend)
- Primary Dependencies: FastAPI, SQLModel, aiokafka, Dapr SDK, APScheduler, websockets
- Storage: PostgreSQL (Neon), Kafka/Redpanda (local Docker + cloud serverless), Redis (Dapr state)
- Testing: pytest (backend), vitest/Jest (frontend), integration + E2E tests
- Performance Targets: <500ms real-time sync, 1000+ events/sec, <100ms WebSocket latency
- Constraints: 100% free-tier services, Dapr local-only, no paid cloud services

### Constitution Compliance
✅ All mandatory Phase 5 principles satisfied:
- Event-Driven Architecture: Every task state change emits Kafka event
- Dapr Integration: Local/K8s development, graceful cloud fallback
- Loose Coupling: Services communicate via events
- Observability: Events traced with correlation_id + user_id
- Cost Optimization: 100% free services (Neon, Redpanda Cloud, Vercel, Render, Civo)
- Recurring Tasks: Automatic spawning on schedule
- Real-Time Updates: WebSocket for live sync

**Gates Passed**: No violations; all principles achievable within implementation

### 12 Phases with Dependencies

```
Phase 5.1: Infrastructure Setup (Local)
  - docker-compose.yml with Redpanda + Redis
  - Multi-stage Dockerfiles (backend, frontend)
  - Base K8s manifests for Minikube
  - Updated requirements.txt

Phase 5.2: Database Schema (depends on 5.1)
  - Task model: +4 fields (due_date, recurrence_rule, is_recurring, next_occurrence)
  - Reminder model: new table with idempotency
  - Alembic migrations
  - Pydantic schemas

Phase 5.3: Event Foundation (depends on 5.1, 5.2) *** CRITICAL PATH ***
  - Kafka event schemas
  - Event publisher (dual-path: Dapr + direct Kafka)
  - Kafka client wrapper (aiokafka)
  - Dapr client wrapper with fallback
  - Event consumer infrastructure
  - Event logging for audit trail
  - Environment-based configuration

Phase 5.4: Recurring Tasks (depends on 5.3)
  - API endpoints: POST/GET/DELETE recurrence
  - RRULE parsing (dateutil.rrule)
  - Scheduler service for task spawning
  - APScheduler integration
  - Dapr binding alternative
  - Frontend UI (RecurrenceForm)

Phase 5.5: Reminders (depends on 5.3)
  - API endpoints: PUT due-date, POST/GET reminders
  - Cron job for reminder checking
  - Event publishing for triggered reminders
  - Idempotency check (notified flag)
  - Frontend UI (DueDatePicker)

Phase 5.6: Real-Time WebSocket (depends on 5.3)
  - FastAPI WebSocket endpoint
  - JWT validation on connect
  - Per-user connection management
  - Event subscriber for broadcasting
  - Frontend WebSocket client with auto-reconnect
  - Fallback to polling if unavailable

Phase 5.7: Kubernetes Local (depends on 5.1, 5.3)
  - Deployment/Service/ConfigMap/Secret manifests
  - Dapr component configuration for K8s
  - Ingress setup (Minikube ingress addon)
  - Port-forward testing

Phase 5.8: Helm Charts (depends on 5.7)
  - Chart.yaml metadata
  - values.yaml with defaults
  - values-dev.yaml and values-prod.yaml
  - Templated K8s resources
  - Conditional Dapr logic

Phase 5.9: Cloud Preparation (depends on 5.1, 5.3, 5.4, 5.5, 5.6)
  - Environment variable management
  - Health check endpoints
  - CORS configuration for cloud domains
  - Graceful Dapr absence handling
  - Multi-provider support

Phase 5.10: Cloud Simple (depends on 5.9) - Parallel to 5.11
  - Redpanda Cloud Serverless setup (FREE tier)
  - Render.com backend configuration
  - Vercel frontend configuration
  - Direct Kafka client (no Dapr)
  - Single instance (FREE 750hrs/month)

Phase 5.11: Cloud K8s (depends on 5.8, 5.9) - Parallel to 5.10
  - Civo cluster creation ($250 FREE credit)
  - Dapr installation on K8s
  - Helm chart deployment
  - Ingress/LoadBalancer setup
  - Redpanda Cloud connection

Phase 5.12: Testing & Documentation (depends on 5.4, 5.5, 5.6, 5.10 OR 5.11)
  - Integration tests for event flows
  - E2E tests for all features
  - Load test (1000+ events/sec)
  - DEPLOYMENT.md (all 3 options)
  - CLOUD_OPTIONS.md comparison
  - Troubleshooting guide
  - Demo video
```

### Project Structure Designed
```
backend/
  - Dockerfile (NEW - multi-stage)
  - routes/
    - websocket.py (NEW)
    - events.py (NEW)
    - tasks.py (UPDATE - add 6 new endpoints)
  - handlers/
    - recurring_tasks.py (NEW)
    - reminders.py (NEW)
    - websocket_handler.py (NEW)
  - services/
    - kafka_client.py (NEW)
    - dapr_client.py (NEW)
    - scheduler.py (NEW)
    - event_log.py (NEW)
    - websocket_manager.py (NEW)

frontend/
  - Dockerfile (NEW - multi-stage)
  - components/realtime/
    - WebSocketProvider.tsx (NEW)
  - components/tasks/
    - RecurrenceForm.tsx (NEW)
    - DueDatePicker.tsx (NEW)
  - lib/
    - websocket-client.ts (NEW)

dapr/
  - pubsub-kafka.yaml (NEW)
  - state-redis.yaml (NEW)
  - bindings-cron.yaml (NEW)

k8s/
  - namespace.yaml (NEW)
  - secrets.yaml (NEW)
  - configmap.yaml (NEW)
  - deployments, services, ingress (NEW)

helm/taskflow/
  - Chart.yaml (NEW)
  - values.yaml (NEW)
  - values-dev.yaml (NEW)
  - values-prod.yaml (NEW)
  - templates/ (NEW - all resources)

migrations/
  - 001_add_recurring_fields.py (NEW)
  - 002_create_reminders_table.py (NEW)
  - 003_add_due_date.py (NEW)

specs/6-event-driven-architecture/
  - DEPLOYMENT.md (NEW)
  - CLOUD_OPTIONS.md (NEW)
  - research.md (NEW - Phase 0)
  - data-model.md (NEW - Phase 1)
  - contracts/ (NEW - API contracts)
```

### Key Implementation Details

**Event Publishing Flow** (dual-path):
1. Database operation succeeds (atomic)
2. Event published (async, best-effort):
   - If USE_DAPR=true: Use Dapr pub/sub
   - If USE_DAPR=false: Use direct aiokafka
3. Consumer processes event
4. Broadcasts to WebSocket connected clients

**Recurring Task Spawning** (cron):
- APScheduler: runs every minute locally
- Dapr Binding: cron trigger in K8s
- Calculates next_occurrence using dateutil.rrule
- Respects user timezone
- Publishes recurring.spawned event
- No duplicates via max_instances=1

**Real-Time Sync** (WebSocket + Event Integration):
- FastAPI WebSocket endpoint with JWT validation
- Per-user subscription to Kafka topics
- Receives events → broadcasts to connected clients
- Auto-reconnect with exponential backoff
- Fallback to HTTP polling if unavailable
- <500ms latency requirement

**Free Tier Strategies**:
- Render 750hrs/month: Single instance, accepts cold starts
- Neon 5GB: Monitor usage, export/import if needed
- Redpanda 10GB/month: Consolidate topics, compress messages
- Civo $250 credit: ~2-3 months cluster runtime
- Dapr local-only: Direct Kafka clients for cloud (no code changes needed)

### Timeline Estimate
**Assuming 4-5 dev hours/week**:
- Phase 5.1: 1 week
- Phase 5.2: 3 days (1.4 weeks cumulative)
- Phase 5.3: 2 weeks (3.4 weeks cumulative) ← Critical Path
- Phase 5.4: 1 week (4.4 weeks)
- Phase 5.5: 4 days (4.95 weeks)
- Phase 5.6: 5 days (5.6 weeks)
- Phase 5.7-5.8: 1.5 weeks (7.1 weeks)
- Phase 5.9: 3 days (7.5 weeks)
- Phase 5.10: 2 days (7.8 weeks)
- Phase 5.11: 2 days (8 weeks)
- Phase 5.12: 2 weeks (10 weeks total)

**TOTAL: ~10 weeks (2.5 months)** with consistent 4-5 hrs/week development

### Cost Breakdown
All $0:
- PostgreSQL (Neon): FREE tier, 5GB
- Kafka/Redpanda Cloud: FREE tier, 10GB/month
- Vercel: FREE tier, unlimited
- Render: FREE tier, 750 hrs/month
- Civo: $250 FREE credit
- Docker, Minikube, Dapr: All open source

**Total Implementation Cost**: $0

### Success Metrics
- Event throughput: 1000+ events/sec ✓ Verifiable
- Real-time latency: <500ms (p95) ✓ Measurable
- WebSocket delivery: <100ms ✓ Verifiable
- Recurring accuracy: Within 5 minutes ✓ Testable
- User isolation: Zero cross-user leakage ✓ Verifiable
- Graceful degradation: Works when services unavailable ✓ Testable
- Deployment: 3 options working (Local, Cloud Simple, Cloud K8s) ✓ Verifiable

---

## PROMPT_TEXT (Verbatim User Input)

```
Generate a detailed implementation plan for Phase 5 based on the specifications.

Organize the plan into logical phases with dependencies, optimized for FREE deployment options:

**Phase 5.1: Infrastructure Setup (Local)**
[... all 12 phases specified with detailed requirements ...]

Each phase should specify:
- Prerequisites
- Tasks to complete
- Files to create/modify
- Testing checkpoints
- Success criteria
- Fallback strategies for free tier limitations
- Cost breakdown ($0 everywhere)
```

## RESPONSE_TEXT (Summary of Plan Created)

Created comprehensive 12-phase implementation plan for Phase 5:

**Plan Document**: specs/6-event-driven-architecture/plan.md (6000+ words)

**Phases Detailed**:
1. Infrastructure Setup: docker-compose + Dockerfiles + K8s base
2. Database Schema: Task extensions + Reminders table + migrations
3. Event Foundation: Kafka/Dapr dual-path + publishers/consumers (CRITICAL PATH)
4. Recurring Tasks: API + RRULE parsing + scheduler + frontend UI
5. Reminders: API + cron jobs + event publishing + notifications
6. WebSocket: Real-time endpoint + auto-reconnect + frontend integration
7. Kubernetes (Local): Manifests + Dapr + Ingress on Minikube
8. Helm Charts: Templated resources + multi-environment support
9. Cloud Preparation: Environment config + health checks + multi-provider
10. Cloud Simple: Vercel + Render + Redpanda Cloud (no Dapr)
11. Cloud K8s: Civo + Dapr + Helm deployment ($250 credit)
12. Testing & Docs: Integration/E2E/load tests + deployment guides + demo

**Dependencies Mapped**: Phase 5.3 (Event Foundation) is critical path; 5.4-5.6 can run parallel; 5.10 and 5.11 can run parallel

**Project Structure**: 50+ new files/modifications designed (backend, frontend, dapr, k8s, helm, migrations, specs)

**Key Implementation Details**:
- Event dual-path: Dapr for local, direct Kafka for cloud (same code path via environment variable)
- Recurring spawning: APScheduler every minute, respects timezone, max_instances=1 prevents duplicates
- Real-time sync: JWT-validated WebSocket, <500ms latency, auto-reconnect, HTTP polling fallback
- Free tier strategies: Render cold starts acceptable, Neon monitoring, Redpanda topic consolidation, Civo 2-3 month credit

**Timeline**: 10 weeks total (2.5 months) @ 4-5 hrs/week development
- Critical path: Phase 5.3 (Event Foundation) gates all dependent features

**Cost**: $0 (100% free-tier services: Neon, Redpanda Cloud, Vercel, Render, Civo)

**Success Metrics**: 1000+ events/sec, <500ms latency, 100+ concurrent WS, zero cross-user leakage, all 3 deployments working

✅ **Plan Status**: READY FOR TASK GENERATION
✅ **Constitution Check**: All mandatory principles satisfied
✅ **Dependencies**: Clear sequencing with parallel opportunities
✅ **Cost**: $0 everywhere
