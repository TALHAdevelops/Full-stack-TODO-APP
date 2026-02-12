# TaskFlow Kubernetes Deployment Guide

This guide covers deploying TaskFlow to a local Kubernetes cluster using Minikube and Helm.

## Prerequisites

Install the following tools before proceeding:

| Tool | Version | Installation |
|------|---------|--------------|
| Docker Desktop | 20.10+ | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |
| Minikube | 1.30+ | [minikube.sigs.k8s.io/docs/start](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | 1.27+ | [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) |
| Helm | 3.12+ | [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |

Verify installations:

```bash
docker --version
minikube version
kubectl version --client
helm version
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Minikube Cluster                        │
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │  Frontend Pod       │    │  Backend Pod        │        │
│  │  (Next.js)          │    │  (FastAPI)          │        │
│  │  Port: 3000         │───▶│  Port: 8000         │───┐    │
│  └─────────────────────┘    └─────────────────────┘   │    │
│           │                          │                │    │
│  ┌────────┴────────┐       ┌────────┴────────┐       │    │
│  │ frontend-svc    │       │ backend-svc     │       │    │
│  │ ClusterIP:80    │       │ ClusterIP:8000  │       │    │
│  └─────────────────┘       └─────────────────┘       │    │
└──────────────────────────────────────────────────────│────┘
                                                       │
                                                       ▼
                                            ┌──────────────────┐
                                            │   Neon Database  │
                                            │   (PostgreSQL)   │
                                            └──────────────────┘
```

## Quick Start

### 1. Start Minikube

```bash
minikube start
```

### 2. Build Docker Images

```bash
# Build frontend image
docker build -t taskflow-frontend:1.0.0 ./frontend

# Build backend image
docker build -t taskflow-backend:1.0.0 ./backend
```

### 3. Load Images into Minikube

```bash
minikube image load taskflow-frontend:1.0.0
minikube image load taskflow-backend:1.0.0
```

### 4. Create Kubernetes Secrets

Create secrets with your actual values:

```bash
kubectl create secret generic taskflow-secrets \
  --from-literal=database-url="postgresql://user:pass@host/db" \
  --from-literal=better-auth-secret="your-32-character-secret-key-here" \
  --from-literal=openai-api-key="sk-your-openai-api-key"
```

### 5. Deploy with Helm

```bash
helm upgrade --install taskflow ./helm -f ./helm/values-dev.yaml
```

### 6. Verify Deployment

```bash
# Check pods are running
kubectl get pods

# Expected output:
# NAME                                 READY   STATUS    RESTARTS   AGE
# taskflow-backend-xxxxx               1/1     Running   0          1m
# taskflow-frontend-xxxxx              1/1     Running   0          1m
```

### 7. Access the Application

Set up port forwarding:

```bash
# Terminal 1 - Frontend
kubectl port-forward svc/taskflow-frontend 3000:80

# Terminal 2 - Backend
kubectl port-forward svc/taskflow-backend 8000:8000
```

Open http://localhost:3000 in your browser.

## Project Structure

```
helm/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration
├── values-dev.yaml         # Development overrides
└── templates/
    ├── _helpers.tpl        # Template helpers
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── configmap.yaml      # Non-sensitive config
    ├── secrets.yaml        # Secret references
    └── NOTES.txt           # Post-install instructions
```

## Configuration

### values.yaml (Defaults)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `replicaCount` | 2 | Number of pod replicas |
| `frontend.image.tag` | 1.0.0 | Frontend image version |
| `backend.image.tag` | 1.0.0 | Backend image version |
| `frontend.resources.limits.memory` | 256Mi | Frontend memory limit |
| `backend.resources.limits.memory` | 512Mi | Backend memory limit |

### values-dev.yaml (Development)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `replicaCount` | 1 | Single replica for local dev |
| `frontend.image.pullPolicy` | Never | Use local image |
| `backend.image.pullPolicy` | Never | Use local image |
| `config.nodeEnv` | development | Enable debug mode |

## Common Operations

### View Logs

```bash
# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend

# Backend logs
kubectl logs -l app.kubernetes.io/component=backend

# Follow logs in real-time
kubectl logs -f deployment/taskflow-backend
```

### Restart Deployment

```bash
kubectl rollout restart deployment/taskflow-frontend
kubectl rollout restart deployment/taskflow-backend
```

### Update Secrets

```bash
# Delete existing secret
kubectl delete secret taskflow-secrets

# Create new secret
kubectl create secret generic taskflow-secrets \
  --from-literal=database-url="new-value" \
  --from-literal=better-auth-secret="new-value" \
  --from-literal=openai-api-key="new-value"

# Restart pods to pick up new secrets
kubectl rollout restart deployment/taskflow-backend
```

### Scale Replicas

```bash
# Scale frontend
kubectl scale deployment/taskflow-frontend --replicas=3

# Scale backend
kubectl scale deployment/taskflow-backend --replicas=3
```

### Check Resource Usage

```bash
kubectl top pods
```

## Troubleshooting

### Pods in CrashLoopBackOff

```bash
# Check pod events
kubectl describe pod <pod-name>

# Check logs from crashed container
kubectl logs <pod-name> --previous
```

**Common causes:**
- Missing or incorrect secrets
- Database connection issues
- Image not loaded into Minikube

### DNS Resolution Errors

If backend can't reach external database:

```bash
# Restart Minikube to reset networking
minikube stop
minikube start

# Delete and recreate pods
kubectl delete pods --all
```

### Image Pull Errors

```bash
# Verify image is loaded
minikube image ls | grep taskflow

# Reload image if missing
minikube image load taskflow-frontend:1.0.0
minikube image load taskflow-backend:1.0.0
```

### Port Already in Use

```bash
# Find process using port
netstat -ano | findstr :3000

# Kill process (Windows)
taskkill /PID <pid> /F

# Or use different ports
kubectl port-forward svc/taskflow-frontend 3001:80
```

## Cleanup

### Uninstall Application

```bash
# Remove Helm release
helm uninstall taskflow

# Delete secrets
kubectl delete secret taskflow-secrets
```

### Stop Minikube

```bash
minikube stop
```

### Delete Minikube Cluster

```bash
minikube delete
```

### Remove Docker Images

```bash
docker rmi taskflow-frontend:1.0.0
docker rmi taskflow-backend:1.0.0
```

## Docker Image Details

### Frontend (taskflow-frontend:1.0.0)

- **Base**: node:20-alpine
- **Build**: Multi-stage (builder + runner)
- **Size**: ~150MB
- **Port**: 3000
- **User**: nextjs (non-root)

### Backend (taskflow-backend:1.0.0)

- **Base**: python:3.12-slim
- **Build**: Multi-stage (builder + runner)
- **Size**: ~250MB
- **Port**: 8000
- **User**: root (with limited packages)

## Security Notes

1. **Secrets Management**: Never commit secrets to version control. Use `kubectl create secret` or external secret managers.

2. **Non-root Containers**: Frontend runs as non-root user. Backend uses minimal packages.

3. **Resource Limits**: All pods have memory/CPU limits to prevent resource exhaustion.

4. **Health Probes**: Liveness and readiness probes ensure traffic only routes to healthy pods.

## Next Steps

- **Production Deployment**: Use a managed Kubernetes service (GKE, EKS, AKS)
- **Ingress Controller**: Add nginx-ingress for proper domain routing
- **TLS/HTTPS**: Configure cert-manager for automatic SSL certificates
- **Monitoring**: Add Prometheus + Grafana for observability
- **CI/CD**: Integrate with GitHub Actions for automated deployments
