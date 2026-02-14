---
id: "PHR-003"
date: 2026-02-14
stage: constitution
title: "Phase V Distributed Cloud-Native Constitution"
status: completed
---

# Prompt History Record: Phase V Constitution Amendment

## Metadata
- **ID**: PHR-003
- **Date**: 2026-02-14
- **Stage**: constitution
- **Title**: Phase V: Distributed Cloud-Native AI Todo System Constitution
- **Version Change**: 3.1.0 → 4.0.0 (MAJOR)

## Summary
User requested creation of a comprehensive constitution for Phase 5, introducing Event-Driven Architecture with Kafka/Redpanda, Dapr service mesh integration, real-time WebSocket updates, recurring tasks with scheduling, and cost-optimized free-tier deployment options (Vercel/Render OR Civo K8s).

## Key Decisions Made

### Architecture Shift (MAJOR Version Bump)
- **Event-Driven Core**: REST API enhanced with Kafka event streaming
- **Loose Coupling**: All inter-service communication via events, not direct HTTP
- **Dapr Integration**: Local/K8s only; graceful degradation for cloud
- **Backward Compatible**: Phase II/III/IV principles unchanged; new principles additive

### New Principles Added (XVIII-XXIV)
1. **Event-Driven Architecture (XVIII)**: Task state changes emit events to Kafka
2. **Dapr Service Mesh (XIX)**: Pub/sub abstraction for local development
3. **Loose Coupling (XX)**: Event-based inter-service communication
4. **Observability (XXI)**: Correlation IDs, structured logging, event audit trail
5. **Cost Optimization (XXII)**: 100% free-tier deployment options
6. **Recurring Tasks (XXIII)**: Scheduling with timezone support
7. **Real-Time Updates (XXIV)**: WebSocket for live task synchronization

### Deployment Strategy
- **Option A (Simple)**: Vercel Frontend + Render Backend + Redpanda Cloud (no K8s)
- **Option B (Kubernetes)**: Civo/Linode free trial + K8s + Dapr sidecars

### Technology Additions
- Kafka/Redpanda for event streaming
- Dapr for pub/sub abstraction (local)
- APScheduler for recurring task scheduling
- aiokafka for async Kafka client
- websockets for real-time updates

## Code Standards Established

### Event Handlers
- Type hints mandatory
- User isolation validation required
- Idempotency checks (event_id deduplication)
- Retry logic with exponential backoff
- Stateless processing

### WebSocket Endpoints
- JWT validation on connect
- User isolation by subscription
- Structured message format with timestamps
- Graceful disconnect handling
- Rate limiting (10 msgs/sec max)

### Event Publishing
- Publish after DB operation succeeds
- Include all metadata (event_id, timestamp, user_id)
- Partition by user_id for ordering
- Graceful degradation on Kafka unavailability

## Testing & Compliance

### Event Integration Tests
- Task creation → event → listener processing
- WebSocket connection → real-time updates
- Kafka unavailability → fallback to database queue
- Multiple users → event isolation verification

### Performance Targets
- 1000+ events/second throughput per instance
- <500ms event latency (p99)
- 100+ concurrent WebSocket connections
- <5 minute recurring task accuracy
- 7-day event retention

## Governance Impact

### Compliance Updates
- Event handlers require user_id validation in code review
- Dapr component YAML in version control (IaC)
- Correlation ID tracing across services mandatory
- Graceful degradation documented in deployment guide

### Breaking Changes (Justified)
- REST API enhanced with event publishing (backward compatible, REST still works)
- WebSocket endpoint added (optional, polling fallback available)
- Recurring task model extension (backward compatible, defaults to no recurrence)

## Files Updated
- `.specify/memory/constitution.md`: Full 4.0.0 version with 7 new principles

## Templates Requiring Updates (Pending)
- `.specify/templates/plan-template.md`: Add event architecture section
- `.specify/templates/spec-template.md`: Add event-driven requirements
- `.specify/templates/tasks-template.md`: Add event handler task category
- README.md: Document Phase V features and deployment options

## Next Steps
1. Generate Phase 5 specification (./sp.specify)
2. Create implementation plan (./sp.plan)
3. Generate task breakdown (./sp.tasks)
4. Implement in order: Kafka integration → Event handlers → WebSocket → Scheduler

---

## PROMPT_TEXT (Verbatim User Input)

```
/sp.constitution

Create a constitution for Phase 5: Distributed Cloud-Native AI Todo System.

Project Context:
- Building on Phase 4 (already have Next.js frontend, FastAPI backend, PostgreSQL with Neon, Better Auth, OpenAI Chatbot with MCP)
- Now adding: Event-Driven Architecture with Kafka, Dapr, Kubernetes deployment, advanced features

Core Principles:
1. Event-Driven Architecture: All significant actions (task created, updated, completed, deleted) must emit events to Kafka
2. Cloud-Native Design: Must work on both Minikube (local) and cloud Kubernetes
3. Loose Coupling: Services communicate via Kafka events and Dapr abstractions
4. Scalability: Support multiple replicas of services, horizontal scaling
5. Observability: All events must be traceable with timestamps and user context
6. Cost Efficiency: Use only free-tier services for deployment

Technology Stack for Phase 5:
- Event Streaming: Kafka (local: Redpanda Docker, cloud: Redpanda Cloud Serverless FREE tier)
- Service Mesh: Dapr for pub/sub, state management, service invocation, secrets (local only)
- Container Orchestration: Kubernetes (local: Minikube, cloud: Civo FREE $250 credit OR Render.com)
- Package Management: Helm charts for K8s deployments
- Existing: Next.js, FastAPI, SQLModel, Neon PostgreSQL, Better Auth, OpenAI Agents SDK, MCP

New Features to Implement:
1. Recurring Tasks - Tasks that repeat on schedule (daily, weekly, monthly)
2. Due Dates & Reminders - Send notifications before tasks are due
3. Real-time Updates - WebSocket connections for live task updates across clients
4. Event-Driven Processing - Async event handlers for all task operations
[... full requirements listed ...]

Constraints:
- Must use 100% FREE services for cloud deployment
- Must demonstrate working deployment on both Minikube AND one cloud option
- All code generated via Claude Code following specs
- No manual coding allowed
- Must document how to adapt for different cloud providers
```

## RESPONSE_TEXT (Summary of Constitution Created)

Created comprehensive Phase 5 Constitution (version 4.0.0, MAJOR bump):

**7 New Principles**:
- XVIII. Event-Driven Architecture: All state changes emit events
- XIX. Dapr Service Mesh: Local pub/sub abstraction
- XX. Loose Coupling: Event-based service communication
- XXI. Observability: Correlation IDs, structured logging, audit trails
- XXII. Cost Optimization: 100% free deployment options
- XXIII. Recurring Tasks: Scheduling with timezone support
- XXIV. Real-Time WebSocket: Live task synchronization

**Technology Stack**: Kafka/Redpanda, Dapr, APScheduler, aiokafka, websockets, Helm

**Deployment Options**:
- Option A: Vercel + Render + Redpanda Cloud Serverless (no K8s)
- Option B: Civo K8s + Dapr sidecars + Redpanda Cloud

**Code Standards**:
- Event handlers: type hints, user isolation, idempotency, retries
- WebSocket: JWT validation, user isolation, rate limiting
- Event publishing: atomic with DB, graceful degradation

**Testing**: Event flows, WebSocket reconnection, load testing (1000 events/sec, 100+ WS connections)

**Documentation**: Architecture.md, Deployment.md, Cloud_Options.md, project structure with dapr/ folder

Constitution includes 24 core principles (I-XVII existing + XVIII-XXIV new), comprehensive coding standards with Python code examples, architectural constraints, performance expectations, testing requirements, non-negotiables, and governance guidelines.
