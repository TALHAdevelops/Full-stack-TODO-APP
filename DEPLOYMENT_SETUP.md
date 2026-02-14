# Deployment Setup Guide — Phase 5: Event-Driven Architecture

## Option 1: Local Development (Docker Compose)

### Prerequisites
- Docker Desktop installed
- Minikube (optional, for K8s testing)

### Steps

```bash
# 1. Copy and configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your Neon DATABASE_URL and BETTER_AUTH_SECRET

# 2. Start all services
docker-compose up --build

# 3. Verify
curl http://localhost:8000/health        # Backend
curl http://localhost:3000               # Frontend
curl http://localhost:9644/v1/cluster    # Redpanda health
```

### Services
| Service | URL | Purpose |
|---------|-----|---------|
| Backend | http://localhost:8000 | FastAPI API |
| Frontend | http://localhost:3000 | Next.js UI |
| Redpanda | localhost:19092 | Kafka broker |
| Redis | localhost:6379 | Dapr state store |

### Cost: $0

---

## Option 2: Cloud Simple (Vercel + Render)

### Prerequisites
- Vercel account (free)
- Render.com account (free)
- Neon PostgreSQL database (free)
- Redpanda Cloud Serverless cluster (free)

### Steps

```bash
# 1. Deploy frontend to Vercel
cd frontend
vercel deploy --prod

# 2. Set Vercel environment variables
#    NEXT_PUBLIC_API_URL = https://your-backend.onrender.com

# 3. Deploy backend to Render
#    Connect GitHub repo → Use render.yaml → Set env vars

# 4. Set Render environment variables
#    DATABASE_URL = your Neon connection string
#    BETTER_AUTH_SECRET = your secret
#    FRONTEND_URL = https://your-app.vercel.app
#    KAFKA_BOOTSTRAP_SERVERS = your Redpanda Cloud bootstrap server
#    KAFKA_SASL_MECHANISM = SCRAM-SHA-256
#    KAFKA_SASL_USERNAME = your Redpanda user
#    KAFKA_SASL_PASSWORD = your Redpanda password
#    KAFKA_SECURITY_PROTOCOL = SASL_SSL
#    USE_DAPR = false
```

### Free Tier Limits
| Service | Limit | Workaround |
|---------|-------|------------|
| Neon DB | 5GB storage | Monitor usage |
| Redpanda Cloud | 10GB/month | Compact events |
| Render | Sleeps after 15min | Cold start ~60s |
| Vercel | Unlimited deploys | None needed |

### Cost: $0

---

## Option 3: Cloud Kubernetes (Civo)

### Prerequisites
- Civo account ($250 free credit)
- kubectl installed
- Helm installed
- Dapr CLI installed

### Steps

```bash
# 1. Create Civo cluster
civo kubernetes create taskflow --size g4s.kube.small --nodes 2

# 2. Get kubeconfig
civo kubernetes config taskflow --save

# 3. Install Dapr
dapr init -k --wait

# 4. Create namespace and secrets
kubectl apply -f k8s/namespace.yaml
kubectl create secret generic taskflow-secrets \
  --from-literal=DATABASE_URL='...' \
  --from-literal=BETTER_AUTH_SECRET='...' \
  -n taskflow

# 5. Deploy via Helm
helm install taskflow ./helm/taskflow \
  -f helm/taskflow/values-prod.yaml \
  -n taskflow

# 6. Verify
kubectl get pods -n taskflow
kubectl port-forward svc/backend-service 8000:8000 -n taskflow
curl http://localhost:8000/health
```

### Cost: $0 (within $250 credit)

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | PostgreSQL connection string |
| BETTER_AUTH_SECRET | Yes | - | JWT signing secret (32+ chars) |
| FRONTEND_URL | No | http://localhost:3000 | Allowed CORS origin |
| KAFKA_BOOTSTRAP_SERVERS | No | localhost:19092 | Kafka broker address |
| REDIS_URL | No | redis://localhost:6379 | Redis connection |
| USE_DAPR | No | false | Enable Dapr sidecar integration |
| KAFKA_SASL_MECHANISM | No | - | Cloud: SCRAM-SHA-256 |
| KAFKA_SASL_USERNAME | No | - | Cloud: Redpanda user |
| KAFKA_SASL_PASSWORD | No | - | Cloud: Redpanda password |
| KAFKA_SECURITY_PROTOCOL | No | - | Cloud: SASL_SSL |
