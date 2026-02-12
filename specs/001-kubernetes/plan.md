# TaskFlow Phase IV Implementation Plan

**Branch**: `001-kubernetes` | **Date**: 2026-02-08 | **Updated**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-kubernetes/spec.md`

---

## Summary

Phase IV transforms the TaskFlow application from locally-running processes into a production-ready containerized deployment on Kubernetes. The Next.js frontend and FastAPI backend will be packaged as Docker containers using multi-stage builds to minimize image sizes (<200MB and <300MB respectively). All Kubernetes resources—Deployments, Services, ConfigMaps, and Secrets—will be defined declaratively in Helm charts following Infrastructure as Code principles. The deployment targets a local Minikube cluster, enabling developers to validate cloud-native patterns before production deployment.

**CRITICAL: Command Automation** — Claude Code executes ALL infrastructure commands automatically (docker build, minikube image load, kubectl create secret, helm install, kubectl port-forward). Users do NOT copy-paste commands. User involvement is limited to: (1) one-time tool installation, (2) providing secret values verbally, and (3) manual browser testing at localhost:3000.

All Phase II & III features (user authentication, task CRUD, AI chatbot) will function identically in the Kubernetes environment, with external Neon PostgreSQL providing data persistence. The architecture supports horizontal scaling (2-3 replicas) and self-healing via Kubernetes controllers.

---

## Technical Context

| Category | Technology | Notes |
|----------|------------|-------|
| **Languages** | TypeScript (frontend), Python 3.13+ (backend), YAML (K8s/Helm) | No changes from Phase III |
| **Primary Dependencies** | Next.js 16+, FastAPI, SQLModel, Better Auth, OpenAI SDK | Application unchanged |
| **Containerization** | Docker | Multi-stage builds required |
| **Base Images** | node:20-alpine (frontend), python:3.13-slim (backend) | Alpine for Node.js, slim for Python |
| **Orchestration** | Minikube (local K8s), kubectl (CLI) | Local development cluster |
| **Package Manager** | Helm 3.14+ | K8s resource management |
| **Storage** | Neon PostgreSQL (external, unchanged) | Not containerized |
| **Testing** | Manual E2E, helm lint, docker build validation | No automated K8s tests in Phase IV |
| **Command Automation** | Claude Code executes all commands | docker, helm, kubectl, minikube |
| **Target Platform** | Local Minikube cluster (Windows/Mac/Linux) | Developer laptops |
| **Performance Goals** | Pod startup <30s, deployment rollout <2 min | Per constitution |
| **Constraints** | Frontend image <200MB, backend <300MB | Image size targets |
| **Scale/Scope** | 2-3 replicas per service | Horizontal scaling support |

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **XIII. Container-First Design** | ✅ Compliant | Multi-stage Dockerfiles for frontend and backend; alpine/slim base images; no hardcoded config; stateless containers |
| **XIV. Kubernetes-Native Patterns** | ✅ Compliant | Deployments (not Pods); Services for networking; ConfigMaps for non-secrets; K8s Secrets for sensitive data; health probes; resource limits |
| **XV. Infrastructure as Code** | ✅ Compliant | All K8s resources in version-controlled Helm templates; declarative configuration; idempotent helm upgrade --install |
| **XVI. Helm Standards** | ✅ Compliant | Helm as package manager; values-driven config; templated manifests; standard chart structure |
| **XVII. Command Automation** | ✅ Compliant | Claude Code executes all docker/helm/kubectl/minikube commands; user never copy-pastes commands; idempotent operations |
| **I. Security First** | ✅ Compliant | Secrets in K8s Secrets (not ConfigMaps); non-root containers; no secrets in Dockerfiles or git |
| **II. Type Safety** | ✅ N/A | Phase IV is infrastructure; no application code changes |
| **Resource Management** | ✅ Compliant | CPU/memory requests and limits defined for all containers |
| **Health Checks** | ✅ Compliant | Liveness and readiness probes on all deployments |

**Gate Status**: ✅ All gates pass. No constitution violations.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-kubernetes/
├── spec.md              # Feature specification (complete)
├── plan.md              # This implementation plan (complete)
├── research.md          # Phase 0 research findings (complete)
├── data-model.md        # Infrastructure data model (complete)
├── quickstart.md        # Developer quickstart guide (complete)
├── contracts/
│   ├── docker-contracts.md   # Docker image contracts (complete)
│   └── helm-contracts.md     # Helm chart contracts (complete)
└── tasks.md             # Task breakdown (pending - use /sp.tasks)
```

### Source Code (repository root)

```text
TALHA-HTFA/
├── frontend/
│   ├── Dockerfile              # NEW: Multi-stage Next.js build
│   ├── .dockerignore           # NEW: Exclude node_modules, .git, .env*
│   └── ... (existing frontend code - unchanged)
│
├── backend/
│   ├── Dockerfile              # NEW: Multi-stage Python build
│   ├── .dockerignore           # NEW: Exclude __pycache__, .venv, .env*
│   └── ... (existing backend code - unchanged)
│
├── helm/                       # NEW: Helm chart directory
│   ├── Chart.yaml              # Helm chart metadata (taskflow v1.0.0)
│   ├── values.yaml             # Default configuration values
│   ├── values-dev.yaml         # Development overrides (replicas=1, pullPolicy=Never)
│   └── templates/
│       ├── _helpers.tpl        # Template helpers (labels, selectors)
│       ├── frontend-deployment.yaml
│       ├── frontend-service.yaml
│       ├── backend-deployment.yaml
│       ├── backend-service.yaml
│       ├── configmap.yaml
│       ├── secrets.yaml        # Template only (real values created manually)
│       └── NOTES.txt           # Post-install instructions
│
├── scripts/                    # NEW: Deployment scripts
│   ├── docker-build.ps1        # Build both Docker images
│   ├── helm-deploy.ps1         # Deploy to Minikube via Helm
│   ├── helm-cleanup.ps1        # Uninstall Helm release
│   └── port-forward.ps1        # Forward ports for local access
│
├── K8S_SETUP.md                # NEW: Kubernetes setup documentation
└── specs/001-kubernetes/       # SDD artifacts (this feature)
```

**Structure Decision**: Web application with separate frontend/backend + new infrastructure layer (helm/, scripts/). Application code remains unchanged; only adding containerization and orchestration artifacts.

---

## Complexity Tracking

> No constitution violations requiring justification. All Phase IV additions align with constitution principles XIII-XVI.

---

## Phase 0: Research & Architecture

### Completed Research Items

All technical unknowns have been resolved in `specs/001-kubernetes/research.md`:

| Topic | Decision | Rationale |
|-------|----------|-----------|
| **Docker Multi-Stage Builds** | Use 2-stage builds (builder → runner) | Reduces image size by excluding build tools from runtime |
| **Kubernetes Resource Type** | Deployments only (no standalone Pods) | Enables self-healing, rolling updates, replica management |
| **Helm Templating** | Go templates with values.yaml + values-dev.yaml | Environment-specific config without manifest duplication |
| **Service Discovery** | K8s DNS (`taskflow-backend:8000`) | Decouples pods; stable endpoints across restarts |
| **Config/Secret Split** | ConfigMaps for URLs/env; Secrets for credentials | Follows K8s best practices; enables RBAC on secrets |
| **Health Probes** | Both liveness (restart) and readiness (traffic) | Prevents traffic to unhealthy pods; auto-recovers crashes |
| **Image Optimization** | Alpine for Node.js, slim for Python | Balances size vs compatibility (Python needs glibc) |
| **Resource Management** | Requests for scheduling, limits for caps | Prevents OOMKill; enables fair scheduling |

### Key Architecture Decisions

1. **External Database**: Neon PostgreSQL remains external to K8s (not containerized)
2. **No Ingress Controller**: Port-forward for local access (ingress is optional/future)
3. **Single Namespace**: All resources in `default` namespace for simplicity
4. **Image Loading**: `minikube image load` (no registry required for local dev)
5. **Manual Secrets**: `kubectl create secret` (never in git)

---

## Phase 1: Design & Contracts

### Contracts Summary

**Docker Contracts** (`contracts/docker-contracts.md`):
- Frontend: node:20-alpine, port 3000, `node server.js`, <200MB
- Backend: python:3.13-slim, port 8000, `uvicorn main:app`, <300MB
- Both: Multi-stage builds, non-root user, no secrets in layers

**Helm Contracts** (`contracts/helm-contracts.md`):
- Chart: apiVersion v2, name `taskflow`, version 1.0.0
- values.yaml: replicaCount, image config, resources, config, secrets reference
- values-dev.yaml: replicaCount=1, pullPolicy=Never
- Templates: deployments, services, configmap, secrets (placeholder), NOTES.txt

**K8s Resource Contracts** (`data-model.md`):
- Labels: `app: taskflow`, `component: frontend|backend`
- Services: frontend (NodePort 80→3000), backend (ClusterIP 8000→8000)
- ConfigMap: FRONTEND_URL, BACKEND_URL, NODE_ENV, LOG_LEVEL
- Secret: database-url, better-auth-secret, openai-api-key

### Image Naming Convention

```
<repository>:<tag>
taskflow-frontend:1.0.0
taskflow-backend:1.0.0
```

- Semantic versioning required
- Never use `:latest`
- Minikube: `imagePullPolicy: Never` (local images)

---

## Phase 2: Implementation Workflow

> **Command Automation**: Claude Code executes ALL infrastructure commands in this phase. User does NOT copy-paste commands.

### PHASE A: Docker Setup (T-401 to T-410) — 10 Tasks

**Objective**: Create and test Dockerfiles for frontend and backend.

**Claude Code Executes**:
- `docker build -t taskflow-frontend:1.0.0 ./frontend`
- `docker build -t taskflow-backend:1.0.0 ./backend`
- `docker images | grep taskflow` (verification)
- `docker run -p 3000:3000 taskflow-frontend:1.0.0` (standalone test)
- `docker run -p 8000:8000 taskflow-backend:1.0.0` (standalone test)

| Task ID | Task | Dependencies | Deliverable |
|---------|------|--------------|-------------|
| T-401 | Create frontend/.dockerignore | None | .dockerignore file |
| T-402 | Create frontend/Dockerfile (multi-stage) | T-401 | Dockerfile |
| T-403 | **[Claude Code]** Build frontend Docker image | T-402 | taskflow-frontend:1.0.0 |
| T-404 | **[Claude Code]** Verify frontend image size (<200MB) | T-403 | Size validation |
| T-405 | **[Claude Code]** Test frontend image standalone | T-404 | Container runs on 3000 |
| T-406 | Create backend/.dockerignore | None | .dockerignore file |
| T-407 | Create backend/Dockerfile (multi-stage) | T-406 | Dockerfile |
| T-408 | **[Claude Code]** Build backend Docker image | T-407 | taskflow-backend:1.0.0 |
| T-409 | **[Claude Code]** Verify backend image size (<300MB) | T-408 | Size validation |
| T-410 | **[Claude Code]** Test backend image standalone | T-409 | Container runs on 8000 |

**Acceptance**: Both images build without errors, meet size targets, and run correctly with `docker run`.

---

### PHASE B: Helm Charts (T-411 to T-425) — 15 Tasks

**Objective**: Create Helm chart structure with all K8s templates.

**Claude Code Executes**:
- `helm lint ./helm/` (validation)
- `helm template taskflow ./helm/` (dry-run to verify YAML output)

| Task ID | Task | Dependencies | Deliverable |
|---------|------|--------------|-------------|
| T-411 | Create helm/Chart.yaml | None | Chart metadata |
| T-412 | Create helm/values.yaml | T-411 | Default values |
| T-413 | Create helm/values-dev.yaml | T-412 | Dev overrides |
| T-414 | Create helm/templates/_helpers.tpl | T-411 | Template helpers |
| T-415 | Create frontend-deployment.yaml | T-414 | Frontend Deployment |
| T-416 | Create frontend-service.yaml | T-415 | Frontend Service |
| T-417 | Create backend-deployment.yaml | T-414 | Backend Deployment |
| T-418 | Create backend-service.yaml | T-417 | Backend Service |
| T-419 | Create configmap.yaml | T-414 | ConfigMap template |
| T-420 | Create secrets.yaml (placeholder) | T-414 | Secret template |
| T-421 | Create NOTES.txt | T-416, T-418 | Post-install help |
| T-422 | Add liveness probe to frontend | T-415 | Health probe config |
| T-423 | Add readiness probe to frontend | T-422 | Health probe config |
| T-424 | Add liveness/readiness to backend | T-417 | Health probe config |
| T-425 | **[Claude Code]** Validate Helm chart with `helm lint` | T-421 | Lint passes |

**Acceptance**: `helm lint ./helm/` passes with zero errors.

---

### PHASE C: Minikube Deployment (T-426 to T-435) — 10 Tasks

**Objective**: Deploy application to Minikube and verify functionality.

**Claude Code Executes**:
- `minikube status` (verify cluster running)
- `minikube image load taskflow-frontend:1.0.0`
- `minikube image load taskflow-backend:1.0.0`
- `kubectl create secret generic taskflow-secrets --from-literal=database-url=... --from-literal=better-auth-secret=...` (user provides values)
- `helm upgrade --install taskflow ./helm/ -f ./helm/values-dev.yaml`
- `kubectl get pods -w` (watch pods reach Running)
- `kubectl get services` (verify services created)
- `kubectl logs deployment/taskflow-backend` (if debugging needed)
- `kubectl port-forward svc/taskflow-frontend 3000:3000` (for user testing)
- `kubectl port-forward svc/taskflow-backend 8000:8000` (for API access)

| Task ID | Task | Dependencies | Deliverable |
|---------|------|--------------|-------------|
| T-426 | **[Claude Code]** Verify Minikube cluster running | None | Running cluster |
| T-427 | **[Claude Code]** Load frontend image into Minikube | T-405, T-426 | Image available |
| T-428 | **[Claude Code]** Load backend image into Minikube | T-410, T-426 | Image available |
| T-429 | **[Claude Code]** Create K8s secrets (user provides values) | T-426 | taskflow-secrets |
| T-430 | **[Claude Code]** Install Helm chart | T-425, T-427, T-428, T-429 | Deployed release |
| T-431 | **[Claude Code]** Verify frontend pods Running | T-430 | Pods healthy |
| T-432 | **[Claude Code]** Verify backend pods Running | T-430 | Pods healthy |
| T-433 | **[Claude Code]** Setup port-forward to frontend | T-431 | localhost:3000 accessible |
| T-434 | **[Claude Code]** Setup port-forward to backend | T-432 | localhost:8000 accessible |
| T-435 | **[Claude Code]** Verify frontend-backend communication | T-433, T-434 | API calls succeed |

**Acceptance**: All pods Running, services accessible via port-forward, API communication working.

---

### PHASE D: Testing & Documentation (T-436 to T-437) — 2 Tasks

**Objective**: Validate all features and document deployment.

**User Manual Actions**:
- Open browser to http://localhost:3000
- Test signup, signin, task CRUD, AI chatbot
- Verify all Phase III features work identically

| Task ID | Task | Dependencies | Deliverable |
|---------|------|--------------|-------------|
| T-436 | **[User]** Manual E2E testing of all Phase III features | T-435 | Test results |
| T-437 | Write K8S_SETUP.md documentation | T-436 | Setup guide |

**Acceptance**: All Phase III features work identically in K8s; documentation complete.

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Docker images too large (>200/300MB) | Medium | Low | Multi-stage builds; alpine/slim bases; .dockerignore to exclude dev files |
| Pods can't connect to Neon DB | Medium | High | Verify DATABASE_URL secret; test connection locally first; check SSL params |
| Secrets not injected correctly | Medium | High | Use `kubectl create secret`; verify with `kubectl exec env`; document manual creation |
| Helm syntax/template errors | Low | Medium | Run `helm lint` frequently; use `helm template` dry-run; validate YAML syntax |
| Pod startup slow/timeout | Medium | Medium | Increase initialDelaySeconds; optimize Dockerfile layers; reduce image size |
| Service DNS resolution fails | Low | High | Verify service name matches; check CoreDNS; use full FQDN if needed |
| Image pull failures in Minikube | Medium | Medium | Use `imagePullPolicy: Never`; run `minikube image load` before deploy |

---

## Success Validation

| Acceptance Test | Criteria | Verification Method |
|-----------------|----------|---------------------|
| **Docker Images Build** | Frontend <200MB, backend <300MB, no errors | `docker images \| grep taskflow` |
| **Helm Chart Valid** | `helm lint` passes with zero errors | `helm lint ./helm/` |
| **Pods Running** | All pods reach Running state within 2 min | `kubectl get pods -w` |
| **Services Accessible** | Frontend at localhost:3000, backend at localhost:8000 | `kubectl port-forward` + curl |
| **Feature Parity** | Signup, signin, task CRUD, chatbot work identically | Manual testing |
| **Scaling Works** | Scale to 3 replicas, pods auto-restart on deletion | `kubectl scale`, `kubectl delete pod` |
| **Data Persists** | Tasks persist across pod restarts | Delete pod, verify data still exists |

---

## Generated Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Feature Spec | `specs/001-kubernetes/spec.md` | ✅ Complete |
| Implementation Plan | `specs/001-kubernetes/plan.md` | ✅ Complete |
| Research Document | `specs/001-kubernetes/research.md` | ✅ Complete |
| Data Model | `specs/001-kubernetes/data-model.md` | ✅ Complete |
| Quickstart Guide | `specs/001-kubernetes/quickstart.md` | ✅ Complete |
| Docker Contracts | `specs/001-kubernetes/contracts/docker-contracts.md` | ✅ Complete |
| Helm Contracts | `specs/001-kubernetes/contracts/helm-contracts.md` | ✅ Complete |
| Task Breakdown | `specs/001-kubernetes/tasks.md` | ⏳ Pending (use `/sp.tasks`) |

---

## Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to generate detailed task breakdown
2. **Implement Phase A**: Create Dockerfiles and build images
3. **Implement Phase B**: Create Helm chart structure and templates
4. **Implement Phase C**: Deploy to Minikube and verify
5. **Implement Phase D**: E2E testing and documentation

---

**Plan Status**: ✅ Ready for Implementation
**Estimated Tasks**: 37 (T-401 to T-437)
**Branch**: `001-kubernetes`
