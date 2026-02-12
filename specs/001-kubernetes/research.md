# Phase IV Research & Architecture Decisions

**Date**: 2026-02-07
**Feature**: TaskFlow Phase IV - Local Kubernetes Deployment
**Purpose**: Document all technical decisions and architecture patterns for containerization and K8s deployment

## Docker Multi-Stage Builds

**Decision**: Use multi-stage Dockerfiles with separate builder and runtime stages for both frontend (Next.js) and backend (FastAPI).

**Rationale**:
- **Size Reduction**: Build tools (compilers, npm, pip, dev dependencies) add 500MB+ to images but aren't needed at runtime
- **Security**: Fewer binaries in runtime image = smaller attack surface
- **Performance**: Smaller images load faster into Minikube and pull faster from registries
- **Separation of Concerns**: Build stage handles compilation, runtime stage handles execution

**Alternatives Considered**:
- **Single-stage builds**: Rejected because they include build tools (gcc, make, node dev deps) in final image, bloating size by 3-5x
- **External build scripts**: Rejected because Dockerfile multi-stage is Docker-native and more portable

**Implementation Notes**:
- **Frontend**: Stage 1 (node:20-alpine) runs `npm ci` and `npm run build`, Stage 2 copies only .next/standalone output
- **Backend**: Stage 1 (python:3.13-slim) installs build deps and compiles wheels, Stage 2 copies only site-packages
- Use `COPY --from=builder` to transfer only necessary artifacts between stages
- Name stages explicitly (AS builder, AS runner) for clarity

---

## Kubernetes Deployments vs Pods

**Decision**: Use Deployment resources exclusively; never create standalone Pods.

**Rationale**:
- **Self-Healing**: Deployments ensure replica count is maintained; if a Pod crashes, Deployment controller creates replacement
- **Rolling Updates**: Deployments support declarative updates with zero downtime via rolling update strategy
- **Replica Management**: Deployments handle scaling (kubectl scale, HPA) automatically
- **Version Control**: Deployments track revision history and support rollback

**Alternatives Considered**:
- **Standalone Pods**: Rejected because they have no controller; if pod dies, it's gone (no auto-restart)
- **ReplicaSets directly**: Rejected because Deployments provide superset of ReplicaSet functionality plus update management

**Implementation Notes**:
- Define `replicas: 2` in Deployment spec for redundancy
- Use `strategy.type: RollingUpdate` with `maxUnavailable: 1, maxSurge: 1`
- Label Pods with `app: taskflow, component: frontend|backend` for selector matching
- Deployments create ReplicaSets automatically; don't manage ReplicaSets manually

---

## Helm Templating

**Decision**: Use Helm 3 with Go template syntax for environment-specific configuration via values files.

**Rationale**:
- **DRY Manifests**: Single Deployment template works for dev/staging/prod via values substitution
- **Environment Parity**: values-dev.yaml and values-prod.yaml ensure consistent structure, different values
- **Version Control**: Helm tracks releases and enables rollback (`helm rollback`)
- **Packaging**: Helm charts are portable, shareable units of K8s applications

**Alternatives Considered**:
- **Kustomize**: Rejected because Helm's values files are more explicit for multiple environments
- **Raw kubectl apply**: Rejected because it requires manual manifest duplication per environment

**Implementation Notes**:
- Use `{{ .Values.replicaCount }}` for values substitution
- Use `{{ .Release.Name }}-frontend` for dynamic resource naming
- Use `{{- if .Values.ingress.enabled }}` for conditional resources
- Validate with `helm lint` and `helm template` before install
- Common pitfall: Forgetting `|` for multi-line strings causes YAML parse errors

---

## Kubernetes Service Discovery

**Decision**: Use ClusterIP Services with Kubernetes DNS for internal service-to-service communication.

**Rationale**:
- **Stable Endpoints**: Service IPs are stable across Pod restarts; Pods get ephemeral IPs
- **Load Balancing**: Service distributes traffic across healthy Pod replicas automatically
- **DNS Integration**: Service name resolves to ClusterIP via kube-dns/CoreDNS (e.g., `http://taskflow-backend:8000`)
- **Decoupling**: Pods don't need to know other Pod IPs; reference service name only

**Alternatives Considered**:
- **Pod IPs directly**: Rejected because Pod IPs change on restart, breaking connections
- **Ingress for internal traffic**: Rejected because Ingress is for external traffic; overkill for pod-to-pod

**Service Type Selection**:
- **ClusterIP** (default): Internal-only access; use for backend API (not exposed outside cluster)
- **NodePort**: Exposes service on each node's IP at static port; use for frontend in Minikube (port-forward alternative)
- **LoadBalancer**: Cloud provider creates external LB; not applicable to Minikube

**Implementation Notes**:
- Frontend accesses backend via `http://taskflow-backend.default.svc.cluster.local:8000` (or shorthand `http://taskflow-backend:8000`)
- Services use `selector: {app: taskflow, component: backend}` to find Pods
- Service `port` is external, `targetPort` is container port (e.g., `port: 80, targetPort: 8000`)

---

## ConfigMaps vs Secrets

**Decision**: Use ConfigMaps for non-sensitive configuration, Secrets for sensitive data.

**Data Classification**:

**ConfigMaps**:
- `FRONTEND_URL=http://taskflow-frontend:3000`
- `BACKEND_URL=http://taskflow-backend:8000`
- `NODE_ENV=production`
- `LOG_LEVEL=info`

**Secrets**:
- `DATABASE_URL=postgresql://user:pass@neon.tech/db` (contains password)
- `BETTER_AUTH_SECRET=<32-char-random>` (JWT signing key)
- `OPENAI_API_KEY=sk-...` (API credentials)

**Rationale**:
- **Security Posture**: Secrets are base64-encoded (not encrypted) but K8s RBAC can restrict access to Secrets only
- **Audit Trail**: Separate resources for sensitive data enable better auditing
- **Convention**: K8s best practice distinguishes config (ConfigMap) from credentials (Secret)

**Injection Methods**:
```yaml
# ConfigMap injection (envFrom)
envFrom:
- configMapRef:
    name: taskflow-config

# Secret injection (env + secretKeyRef)
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: taskflow-secrets
      key: database-url
```

**Implementation Notes**:
- Secrets are base64-encoded in YAML (`echo -n 'value' | base64`) but decoded when injected into Pods
- **NEVER commit real secret values to git**; use placeholder values and document manual creation
- Use `kubectl create secret generic taskflow-secrets --from-literal=database-url=...` for manual creation
- ConfigMaps can be updated and reflected via pod restart (`kubectl rollout restart deployment`)

---

## Health Checks (Liveness & Readiness Probes)

**Decision**: Define both liveness and readiness probes for all containers.

**Probe Types**:

**Liveness Probe**:
- **Purpose**: Detects if container is stuck/deadlocked and needs restart
- **Action on Failure**: Kubernetes kills and restarts the container
- **Use Case**: Detect hung processes, deadlocks, infinite loops

**Readiness Probe**:
- **Purpose**: Detects if container is ready to serve traffic
- **Action on Failure**: Kubernetes removes Pod from Service endpoints (no traffic routed)
- **Use Case**: Slow startup, database connection not ready, dependency unavailable

**Rationale**:
- **Availability**: Readiness probes prevent traffic to unhealthy Pods, maintaining uptime
- **Self-Healing**: Liveness probes automatically recover from failures without manual intervention
- **Zero-Downtime Deployments**: Readiness probes ensure new Pods are healthy before old Pods terminate

**Configuration Best Practices**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30   # Wait for app startup
  periodSeconds: 10         # Check every 10s
  timeoutSeconds: 5         # Fail if no response in 5s
  failureThreshold: 3       # 3 consecutive failures = restart

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10   # Shorter than liveness
  periodSeconds: 5          # More frequent checks
  failureThreshold: 3
```

**Implementation Notes**:
- **Backend**: `/health` endpoint returns 200 OK if database connection succeeds
- **Frontend**: HTTP GET on port 3000 (or TCP socket probe if no health endpoint)
- **initialDelaySeconds**: Set based on actual startup time (measure with `time docker run`)
- **Avoid false positives**: Set failureThreshold ≥ 3 to tolerate transient issues

---

## Image Optimization

**Decision**: Use alpine variants for Node.js (node:20-alpine), slim variants for Python (python:3.13-slim).

**Rationale**:
- **Alpine for Node.js**: 40MB base vs 180MB debian base; Next.js doesn't need glibc-specific features
- **Slim for Python**: 120MB vs 180MB full; alpine + Python has compilation issues with native extensions (cryptography, psycopg2)
- **Layer Caching**: `COPY package*.json` before `COPY . .` caches npm install layer
- **.dockerignore**: Exclude node_modules, .git, __pycache__ from build context (faster uploads to Docker daemon)

**Size Targets**:
- Frontend: <200MB (multi-stage Next.js standalone build)
- Backend: <300MB (slim Python + minimal deps)

**Best Practices**:
```dockerfile
# Good: Separate dependency install from code copy
COPY package*.json ./
RUN npm ci --only=production
COPY . .

# Bad: Single COPY invalidates cache on any code change
COPY . .
RUN npm ci
```

**npm ci vs npm install**:
- **npm ci**: Deletes node_modules, installs from package-lock.json (deterministic, faster in CI)
- **npm install**: Respects existing node_modules, updates package-lock.json (use in dev only)

**Implementation Notes**:
- Use `RUN npm ci --only=production` in runtime stage to exclude devDependencies
- Backend: `pip install --no-cache-dir -r requirements.txt` to avoid caching pip downloads in image
- Frontend standalone mode: `npm run build` with `output: 'standalone'` in next.config.js generates minimal runtime

---

## Resource Management

**Decision**: Define both resource requests and limits for all containers.

**Concepts**:

**Requests** (Minimum Guaranteed):
- Kubernetes scheduler uses requests to decide which node can fit the Pod
- Pod won't be scheduled if no node has enough CPU/memory to meet requests
- Determines QoS class (BestEffort, Burstable, Guaranteed)

**Limits** (Maximum Allowed):
- Container can't exceed limit
- **CPU**: Throttled if exceeded (process slowed down)
- **Memory**: OOMKilled if exceeded (container terminated)

**Rationale**:
- **Prevent Resource Starvation**: Requests ensure Pods have minimum resources
- **Prevent Noisy Neighbors**: Limits prevent one Pod from consuming all node resources
- **Predictable Performance**: Right-sized requests/limits ensure consistent response times

**Recommended Values**:
```yaml
# Frontend (Next.js)
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"       # 0.1 CPU core
  limits:
    memory: "256Mi"
    cpu: "250m"

# Backend (FastAPI)
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**QoS Classes**:
- **Guaranteed**: requests == limits for all containers (highest priority, last to be evicted)
- **Burstable**: requests < limits (medium priority)
- **BestEffort**: no requests/limits (lowest priority, first to be evicted)

**Implementation Notes**:
- Start with conservative estimates, monitor with `kubectl top pod` and adjust
- Memory limits too low → OOMKilled → Pod restart loop
- CPU limits too low → slow response times but no crash
- Minikube default: 2 CPUs, 4GB RAM; ensure total requests fit within this

---

## Summary

All technical unknowns for Phase IV have been resolved:
- ✅ Docker multi-stage builds minimize image size and improve security
- ✅ Kubernetes Deployments provide self-healing and rolling updates
- ✅ Helm templating enables environment-specific configuration
- ✅ Service discovery via Kubernetes DNS decouples Pods
- ✅ ConfigMaps for config, Secrets for credentials (never in git)
- ✅ Health probes ensure availability and enable self-healing
- ✅ Alpine/slim base images, layer caching, and .dockerignore optimize build
- ✅ Resource requests/limits prevent starvation and ensure predictability

**Next Steps**: Proceed to Phase 1 (Design & Contracts) to define data models and API contracts.
