# TaskFlow Deployment Guide

## Prerequisites
- GitHub repo: https://github.com/TALHAdevelops/Full-stack-TODO-APP
- Neon PostgreSQL database (already configured)
- Migrations already applied

## Option 1: Cloud Simple (Render + Vercel) - FREE

### Step 1: Deploy Backend to Render

1. Go to https://render.com and sign up / log in with GitHub
2. Click **"New +"** > **"Blueprint"**
3. Connect your GitHub repo: `TALHAdevelops/Full-stack-TODO-APP`
4. Render will auto-detect `render.yaml` and configure the service
5. Set the required **secret** environment variables when prompted:
   - `DATABASE_URL`: your Neon PostgreSQL connection string
   - `BETTER_AUTH_SECRET`: your auth secret
6. Click **"Apply"** to deploy
7. Wait for the build to complete (~3-5 min)
8. Note your backend URL (e.g., `https://taskflow-backend-xxxx.onrender.com`)
9. Verify: visit `https://your-backend-url.onrender.com/health`
   - Should return: `{"status":"healthy","version":"5.0.0"}`

### Step 2: Deploy Frontend to Vercel

**Option A: Via Vercel Dashboard (Recommended)**
1. Go to https://vercel.com and sign up / log in with GitHub
2. Click **"Add New Project"**
3. Import: `TALHAdevelops/Full-stack-TODO-APP`
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
5. Add **Environment Variables**:
   - `NEXT_PUBLIC_API_URL` = `https://your-render-backend-url.onrender.com`
   - `NEXT_PUBLIC_WS_URL` = `wss://your-render-backend-url.onrender.com`
   - `NEXT_PUBLIC_APP_URL` = `https://your-vercel-project.vercel.app`
   - `BETTER_AUTH_SECRET` = your auth secret (same as backend)
6. Click **"Deploy"**
7. Wait for build (~1-2 min)

**Option B: Via Vercel CLI**
```bash
cd frontend
vercel login
vercel --prod \
  -e NEXT_PUBLIC_API_URL=https://your-render-backend-url.onrender.com \
  -e NEXT_PUBLIC_WS_URL=wss://your-render-backend-url.onrender.com \
  -e BETTER_AUTH_SECRET=your_secret
```

### Step 3: Update Backend CORS

After both are deployed, update the Render backend's `FRONTEND_URL` env var:
- Go to Render Dashboard > taskflow-backend > Environment
- Set `FRONTEND_URL` = `https://your-vercel-project.vercel.app`
- Redeploy

---

## Option 2: Local Docker Compose

```bash
# Make sure Docker Desktop is running
# Create root .env file with:
#   DATABASE_URL=your_neon_url
#   BETTER_AUTH_SECRET=your_secret
#   USE_DAPR=false

docker-compose up --build

# Services:
#   Frontend: http://localhost:3000
#   Backend:  http://localhost:8000
#   Redpanda: localhost:19092
#   Redis:    localhost:6379
```

---

## Option 3: Kubernetes (Civo)

### Prerequisites
- Civo account (https://civo.com - $250 free credit)
- kubectl installed
- Helm installed

### Steps
```bash
# 1. Create Civo cluster
civo kubernetes create taskflow --size g4s.kube.small --nodes 2 --wait

# 2. Get kubeconfig
civo kubernetes config taskflow --save

# 3. Create namespace and secrets
kubectl apply -f k8s/namespace.yaml
# Edit k8s/secrets.yaml with your base64-encoded secrets first
kubectl apply -f k8s/secrets.yaml

# 4. Deploy with Helm
helm install taskflow ./helm -f helm/values-prod.yaml \
  --namespace taskflow \
  --set backend.image.tag=latest \
  --set frontend.image.tag=latest

# 5. Get external IP
kubectl get ingress -n taskflow
```

---

## Environment Variables Reference

| Variable | Required | Where | Description |
|----------|----------|-------|-------------|
| `DATABASE_URL` | Yes | Backend | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | Both | JWT signing secret (must match) |
| `FRONTEND_URL` | Yes | Backend | Frontend origin for CORS |
| `NEXT_PUBLIC_API_URL` | Yes | Frontend | Backend API base URL |
| `NEXT_PUBLIC_WS_URL` | No | Frontend | WebSocket URL (for real-time) |
| `NEXT_PUBLIC_APP_URL` | No | Frontend | Frontend public URL |
| `USE_DAPR` | No | Backend | Enable Dapr sidecar (default: false) |
| `KAFKA_BOOTSTRAP_SERVERS` | No | Backend | Kafka/Redpanda broker address |
| `REDIS_URL` | No | Backend | Redis connection URL |

## Costs
- **Render Free Tier**: $0/month (backend spins down after 15 min inactivity)
- **Vercel Free Tier**: $0/month (hobby plan)
- **Neon Free Tier**: $0/month (0.5 GB storage, 1 compute)
- **Total**: $0/month
