# Data Model - Phase IV Kubernetes Deployment

**Date**: 2026-02-07
**Feature**: TaskFlow Phase IV - Local Kubernetes Deployment
**Note**: Phase IV does not introduce new database entities. All data models from Phase II/III remain unchanged. This document describes the **infrastructure data model** (Kubernetes resources, not database schemas).

## Infrastructure Entities

### Docker Images

**taskflow-frontend:1.0.0**
- **Type**: Container Image
- **Base**: node:20-alpine
- **Size Target**: <200MB
- **Exposed Port**: 3000
- **Entry Command**: `node server.js` (Next.js standalone)
- **Build Artifacts**: .next/standalone/ (minimal Next.js runtime)
- **Environment Variables**: BACKEND_URL, NODE_ENV (from ConfigMap)

**taskflow-backend:1.0.0**
- **Type**: Container Image
- **Base**: python:3.13-slim
- **Size Target**: <300MB
- **Exposed Port**: 8000
- **Entry Command**: `uvicorn main:app --host 0.0.0.0 --port 8000`
- **Build Artifacts**: All backend/ Python code + site-packages
- **Environment Variables**: DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY (from Secret)

---

### Kubernetes Deployments

**Deployment: taskflow-frontend**
- **apiVersion**: apps/v1
- **Replicas**: 2 (configurable via values.yaml)
- **Selector**: `app: taskflow, component: frontend`
- **Container**: taskflow-frontend:1.0.0
- **Ports**: containerPort 3000
- **Resources**:
  - Requests: 100m CPU, 128Mi memory
  - Limits: 250m CPU, 256Mi memory
- **Probes**:
  - Liveness: TCP socket on port 3000, initialDelay 30s
  - Readiness: TCP socket on port 3000, initialDelay 10s
- **ConfigMap Injection**: envFrom → taskflow-config

**Deployment: taskflow-backend**
- **apiVersion**: apps/v1
- **Replicas**: 2 (configurable via values.yaml)
- **Selector**: `app: taskflow, component: backend`
- **Container**: taskflow-backend:1.0.0
- **Ports**: containerPort 8000
- **Resources**:
  - Requests: 250m CPU, 256Mi memory
  - Limits: 500m CPU, 512Mi memory
- **Probes**:
  - Liveness: HTTP GET /health on port 8000, initialDelay 30s
  - Readiness: HTTP GET /health on port 8000, initialDelay 10s
- **ConfigMap Injection**: envFrom → taskflow-config
- **Secret Injection**: env → DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY from taskflow-secrets

---

### Kubernetes Services

**Service: taskflow-frontend**
- **apiVersion**: v1
- **Type**: NodePort (for local Minikube access)
- **Selector**: `app: taskflow, component: frontend`
- **Ports**:
  - `port: 80` (service port)
  - `targetPort: 3000` (container port)
  - `nodePort: 30000` (optional, assigned by K8s if omitted)
- **DNS Name**: `taskflow-frontend.default.svc.cluster.local`

**Service: taskflow-backend**
- **apiVersion**: v1
- **Type**: ClusterIP (internal only)
- **Selector**: `app: taskflow, component: backend`
- **Ports**:
  - `port: 8000` (service port)
  - `targetPort: 8000` (container port)
- **DNS Name**: `taskflow-backend.default.svc.cluster.local`

---

### Configuration Resources

**ConfigMap: taskflow-config**
- **apiVersion**: v1
- **Data**:
  - `FRONTEND_URL`: http://taskflow-frontend
  - `BACKEND_URL`: http://taskflow-backend:8000
  - `NODE_ENV`: production
  - `LOG_LEVEL`: info

**Secret: taskflow-secrets**
- **apiVersion**: v1
- **Type**: Opaque
- **Data** (base64-encoded):
  - `database-url`: `<Neon PostgreSQL connection string>`
  - `better-auth-secret`: `<32-character random string>`
  - `openai-api-key`: `<OpenAI API key>`
- **Creation Method**: Manual via `kubectl create secret generic` (NEVER committed to git)

---

### Helm Chart

**Chart.yaml**
- **apiVersion**: v2
- **name**: taskflow
- **version**: 1.0.0
- **appVersion**: 1.0.0
- **description**: TaskFlow multi-user todo application with AI chatbot
- **type**: application

**values.yaml (default)**
```yaml
replicaCount: 2

frontend:
  image:
    repository: taskflow-frontend
    tag: "1.0.0"
    pullPolicy: IfNotPresent
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "250m"

backend:
  image:
    repository: taskflow-backend
    tag: "1.0.0"
    pullPolicy: IfNotPresent
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

config:
  frontendUrl: "http://taskflow-frontend"
  backendUrl: "http://taskflow-backend:8000"
  nodeEnv: "production"
  logLevel: "info"

secrets:
  # Values NOT stored here; referenced by name
  secretName: "taskflow-secrets"
```

**values-dev.yaml (development overrides)**
```yaml
replicaCount: 1  # Single replica for dev

frontend:
  image:
    pullPolicy: Never  # Use locally loaded image in Minikube

backend:
  image:
    pullPolicy: Never

config:
  nodeEnv: "development"
  logLevel: "debug"
```

---

## Resource Relationships

```
Helm Chart (taskflow)
├── Chart.yaml (metadata)
├── values.yaml (default config)
├── values-dev.yaml (dev overrides)
└── templates/
    ├── frontend-deployment.yaml
    │   └── References: taskflow-frontend image, taskflow-config ConfigMap
    ├── backend-deployment.yaml
    │   └── References: taskflow-backend image, taskflow-config ConfigMap, taskflow-secrets Secret
    ├── frontend-service.yaml
    │   └── Selects Pods: app=taskflow, component=frontend
    ├── backend-service.yaml
    │   └── Selects Pods: app=taskflow, component=backend
    ├── configmap.yaml
    │   └── Provides: Environment variables for both deployments
    └── secrets.yaml (template only, real values created manually)
        └── Provides: Sensitive environment variables for backend
```

**Service Discovery Flow**:
1. Frontend Pod makes HTTP request to `http://taskflow-backend:8000/api/v1/users/1/tasks`
2. Kubernetes DNS resolves `taskflow-backend` to Service ClusterIP (e.g., 10.96.0.100)
3. Service routes request to one healthy backend Pod (e.g., taskflow-backend-abc123)
4. Backend Pod processes request and returns response

**Scaling Flow**:
1. Update `replicaCount: 3` in values.yaml
2. Run `helm upgrade taskflow ./helm/ -f ./helm/values-dev.yaml`
3. Deployment controller creates 1 new frontend Pod and 1 new backend Pod
4. New Pods pass readiness probes
5. Services automatically include new Pods in load balancing

---

## State and Persistence

**Stateless Containers**:
- Frontend containers have NO local state; all user session state in JWT tokens
- Backend containers have NO local state; all data in external Neon database
- Containers can be killed and recreated without data loss

**External Database**:
- **Provider**: Neon PostgreSQL (cloud-hosted, external to Kubernetes)
- **Connection**: Backend Pods connect via DATABASE_URL secret
- **Schema**: User, Task, Conversation, Message tables (unchanged from Phase III)
- **Persistence**: Data persists across Pod restarts, scaling operations, and cluster recreation

**No Persistent Volumes**:
- No StatefulSets or PersistentVolumeClaims in Phase IV
- All persistent data lives in Neon, not in Kubernetes

---

## Resource Allocation Summary

**Minikube Cluster Requirements**:
- **Total CPU Requests**: 100m (frontend) + 250m (backend) = 350m per replica × 2 replicas = 700m
- **Total Memory Requests**: 128Mi (frontend) + 256Mi (backend) = 384Mi per replica × 2 replicas = 768Mi
- **Recommended Minikube Config**: `minikube start --memory=4096 --cpus=2`

**Image Sizes**:
- taskflow-frontend: ~180MB (Next.js standalone)
- taskflow-backend: ~280MB (Python + FastAPI + SQLModel)
- Total: ~460MB (fits comfortably in Minikube's default storage)

---

## Validation

**Entity Completeness**:
- ✅ All Docker images defined with base, size, ports, commands
- ✅ All Kubernetes Deployments defined with replicas, selectors, probes, resources
- ✅ All Services defined with type, selectors, ports, DNS names
- ✅ ConfigMap and Secret defined with keys and injection methods
- ✅ Helm chart structure defined with Chart.yaml, values files, templates
- ✅ Resource relationships documented
- ✅ State and persistence strategy clarified

**Next Steps**: Generate API contracts (Phase 1 continuation)
