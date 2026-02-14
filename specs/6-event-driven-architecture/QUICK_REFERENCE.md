# Phase 5 Quick Reference: Event-Driven Architecture

## Quick Start Choice Matrix

**Choose your path:**

| You Want To... | Choose | Why |
|---|---|---|
| Learn locally without cloud costs | **Local (Minikube)** | Full Dapr, Redpanda Docker, learn K8s + event streaming |
| Deploy demo quickly to show others | **Cloud Simple** | 5 min setup, Vercel + Render, free tier works |
| Showcase production-ready K8s skills | **Cloud K8s (Civo)** | Full architecture, Dapr, $250 credit lasts 2-3 months |

---

## Key APIs & Events

### REST Endpoints (Unchanged from Phase 4)
```bash
# Existing endpoints
POST   /api/{user_id}/tasks
GET    /api/{user_id}/tasks
PUT    /api/{user_id}/tasks/{id}
DELETE /api/{user_id}/tasks/{id}
PATCH  /api/{user_id}/tasks/{id}/complete

# NEW: Recurring tasks
POST   /api/{user_id}/tasks/{id}/recurrence
GET    /api/{user_id}/tasks/recurring
DELETE /api/{user_id}/tasks/{id}/recurrence

# NEW: Reminders
POST   /api/{user_id}/tasks/{id}/reminders
GET    /api/{user_id}/reminders/pending
PUT    /api/{user_id}/tasks/{id}/due-date

# NEW: WebSocket
GET    /ws/user/{user_id}/tasks  (WebSocket upgrade)
```

### Kafka Topics & Events

| Topic | Event Type | Published By | Consumed By |
|-------|-----------|--------------|------------|
| `tasks.events` | task.created | REST handler | WebSocket notifier, Scheduler |
| `tasks.events` | task.updated | REST handler | WebSocket notifier |
| `tasks.events` | task.deleted | REST handler | WebSocket notifier |
| `tasks.events` | task.completed | REST handler | Scheduler (checks reminders) |
| `tasks.events` | recurring.spawned | Scheduler | WebSocket notifier |
| `reminders.events` | reminder.triggered | Scheduler | WebSocket notifier |

### Event JSON Schema

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task.created|updated|deleted|completed|recurring.spawned|reminder.triggered",
  "user_id": "user-123",
  "aggregate_id": "task-456",
  "timestamp": "2026-02-14T15:30:45Z",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440001",
  "data": {
    "title": "Buy milk",
    "description": "Get 2% milk from grocery store",
    "due_date": "2026-02-15T09:00:00Z",
    "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO",
    "is_recurring": true
  },
  "version": 1
}
```

### WebSocket Message Schema

```json
{
  "type": "task.created|updated|deleted|completed|reminder",
  "data": {
    "id": "task-456",
    "title": "Buy milk",
    "completed": false,
    "due_date": "2026-02-15T09:00:00Z"
  },
  "timestamp": "2026-02-14T15:30:45Z",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

---

## Database Schema Changes

### Task Table (Extended)
```sql
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP NULL;
ALTER TABLE tasks ADD COLUMN recurrence_rule VARCHAR(255) NULL;
ALTER TABLE tasks ADD COLUMN is_recurring BOOLEAN DEFAULT false;
ALTER TABLE tasks ADD COLUMN next_occurrence TIMESTAMP NULL;
CREATE INDEX idx_tasks_next_occurrence ON tasks(next_occurrence)
  WHERE is_recurring = true;
```

### Reminders Table (New)
```sql
CREATE TABLE reminders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  remind_at TIMESTAMP NOT NULL,
  notified BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT now(),

  CONSTRAINT unique_reminder_per_task_time
    UNIQUE (task_id, remind_at)
);

CREATE INDEX idx_reminders_remind_at ON reminders(remind_at);
CREATE INDEX idx_reminders_user_notified
  ON reminders(user_id, notified)
  WHERE notified = false;
```

---

## Environment Variables by Deployment

### Local (Minikube + Dapr)
```bash
DATABASE_URL=postgresql://user:password@neon.tech/dbname
KAFKA_BOOTSTRAP_SERVERS=redpanda:9092
REDIS_URL=redis://redis-service:6379
USE_DAPR=true
ENVIRONMENT=local
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
```

### Cloud Simple (Vercel + Render + Redpanda Cloud)
```bash
DATABASE_URL=postgresql://user:password@neon.tech/dbname
KAFKA_BOOTSTRAP_SERVERS=<your-cluster>.cloud.redpanda.com:9092
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
KAFKA_SASL_USERNAME=<username>
KAFKA_SASL_PASSWORD=<password>
KAFKA_SECURITY_PROTOCOL=SASL_SSL
USE_DAPR=false
ENVIRONMENT=production
```

### Cloud K8s (Civo + Dapr + Redpanda Cloud)
```bash
DATABASE_URL=postgresql://user:password@neon.tech/dbname
KAFKA_BOOTSTRAP_SERVERS=<your-cluster>.cloud.redpanda.com:9092
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
KAFKA_SASL_USERNAME=<username>
KAFKA_SASL_PASSWORD=<password>
KAFKA_SECURITY_PROTOCOL=SASL_SSL
USE_DAPR=true
ENVIRONMENT=production
REDIS_URL=redis://redis-service.taskflow:6379
DAPR_HTTP_PORT=3500
```

---

## Testing Checklist

### Minimum Viable Tests
- [ ] Create task → appears on 2 browser tabs within 500ms
- [ ] Create recurring task → new instance spawns at scheduled time
- [ ] Set reminder → notification sent at reminder time
- [ ] Disconnect WebSocket → auto-reconnect succeeds within 5s
- [ ] Kill Kafka → task creation still works (DB queue fallback)

### Integration Tests
- [ ] Event published → consumer receives → WebSocket delivers
- [ ] Multiple users → events isolated (no data leakage)
- [ ] Event replay → reconstructs task state

### Performance Benchmarks
- [ ] 1000+ events/sec throughput
- [ ] <500ms end-to-end latency
- [ ] 100+ concurrent WebSocket connections

---

## Deployment Quick Steps

### Local Minikube
```bash
# 1. Start Minikube
minikube start --memory=4096 --cpus=2

# 2. Install Dapr
dapr init -k

# 3. Build and deploy
docker build -t taskflow-backend:1.0.0 ./backend
docker build -t taskflow-frontend:1.0.0 ./frontend
minikube image load taskflow-backend:1.0.0
minikube image load taskflow-frontend:1.0.0

# 4. Apply Dapr components
kubectl apply -f dapr/components.yaml

# 5. Deploy via Helm
helm install taskflow ./charts/taskflow -f charts/taskflow/values-dev.yaml

# 6. Port forward
kubectl port-forward svc/taskflow-frontend 3000:3000 &
kubectl port-forward svc/taskflow-backend 8000:8000 &

# Access at http://localhost:3000
```

### Cloud Simple
```bash
# 1. Create Redpanda Cloud Serverless cluster (FREE tier)
# https://redpanda.com/redpanda-cloud

# 2. Create Render account & deploy backend from GitHub
# https://render.com
# - New Web Service → Connect GitHub repo
# - Build command: `docker build -t taskflow-backend .`
# - Environment: Add DATABASE_URL, KAFKA_* credentials
# - Deploy

# 3. Deploy frontend to Vercel from GitHub
# https://vercel.com
# - Import GitHub repo → select frontend root
# - Environment: Add NEXT_PUBLIC_API_URL=<render-backend-url>
# - Deploy

# Total setup time: ~15 minutes
```

### Cloud K8s (Civo)
```bash
# 1. Create Civo cluster (FREE $250 credit)
civo k8s create taskflow-cluster --size g4s.kube.small --nodes 2

# 2. Get kubeconfig
civo k8s config taskflow-cluster --save

# 3. Install Dapr
dapr init -k

# 4. Create secrets
kubectl create namespace taskflow
kubectl create secret generic taskflow-secrets \
  --from-literal=database-url=<neon-url> \
  --from-literal=kafka-brokers=<redpanda-url> \
  -n taskflow

# 5. Deploy via Helm
helm install taskflow ./charts/taskflow -f charts/taskflow/values-prod.yaml -n taskflow

# 6. Configure Ingress for DNS
kubectl apply -f k8s/ingress.yaml

# Total setup time: ~10 minutes
```

---

## Free Tier Limitations & Workarounds

| Service | Limit | Impact | Workaround |
|---------|-------|--------|-----------|
| **Neon PostgreSQL** | 5GB storage, 3 projects | Sufficient for 1000 users | Monitor storage; export & reimport if needed |
| **Redpanda Cloud** | 10GB/month, 3 topics | Good for 1000 events/sec | Consolidate topics; monitor usage |
| **Render.com** | 750 hrs/month, 1 web service | ~1 instance always running | Upgrade to paid for multiple instances |
| **Vercel** | Unlimited bandwidth | Not a bottleneck | No workaround needed |
| **Civo** | $250 credit / $100 Linode | ~2-3 months | Upgrade to paid after credits exhaust |

---

## Troubleshooting Quick Reference

| Problem | Cause | Solution |
|---------|-------|----------|
| Tasks don't sync across devices | WebSocket not connected | Check browser console; ensure server WebSocket endpoint accessible |
| Recurring tasks not spawning | Scheduler pod not running | `kubectl get pods -n taskflow`; check scheduler logs |
| Reminders not sent | Kafka consumer lag too high | Check consumer group lag; may need to scale backend replicas |
| Cold start too slow (Render) | FREE tier spins down after 15min | Expected behavior; upgrade for production |
| Dapr pub/sub errors | Kafka broker unreachable | Check KAFKA_BOOTSTRAP_SERVERS; ensure Redpanda Cloud credentials correct |

---

## Next Steps After Deployment

1. Load test with 1000+ events/sec
2. Test failover (kill pod → K8s restarts)
3. Test data migration (scale to production)
4. Add email/SMS reminders (Phase 5.1)
5. Add task sharing/collaboration (Phase 5.2)
