# TaskFlow Phase IV Task Breakdown

**Feature**: Local Kubernetes Deployment
**Branch**: `001-kubernetes`
**Created**: 2026-02-08
**Updated**: 2026-02-08
**Total Tasks**: 37 (T-401 to T-437)

> **COMMAND AUTOMATION**: Claude Code executes ALL infrastructure commands automatically.
> User does NOT copy-paste commands. User involvement limited to:
> 1. One-time tool installation (Docker, Minikube, kubectl, Helm)
> 2. Providing secret values when prompted
> 3. Manual browser testing at http://localhost:3000

---

## Status Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 37 |
| Completed | 37 |
| In Progress | 0 |
| Remaining | 0 |

---

## Phase Overview

| Phase | Task Range | Tasks | Description |
|-------|------------|-------|-------------|
| **A** | T-401 to T-410 | 10 | Docker Setup (Dockerfiles, images, validation) |
| **B** | T-411 to T-425 | 15 | Helm Charts & K8s Manifests |
| **C** | T-426 to T-435 | 10 | Minikube Deployment & Verification |
| **D** | T-436 to T-437 | 2 | Testing & Documentation |

---

## Phase A: Docker Setup (T-401 to T-410)

**Objective**: Create optimized Docker images for frontend and backend with multi-stage builds.

**Claude Code Executes**:
- `docker build -t taskflow-frontend:1.0.0 ./frontend`
- `docker build -t taskflow-backend:1.0.0 ./backend`
- `docker images | grep taskflow` (verification)
- `docker run -p 3000:3000 taskflow-frontend:1.0.0` (standalone test)
- `docker run -p 8000:8000 -e DATABASE_URL=... taskflow-backend:1.0.0` (standalone test)

| ID | Task Title | Status | Executor | Dependency |
|----|------------|--------|----------|------------|
| T-401 | Create frontend/.dockerignore | [x] | Claude | None |
| T-402 | Create frontend/Dockerfile with multi-stage build | [x] | Claude | T-401 |
| T-403 | **Build frontend Docker image** | [x] | **Claude Code** | T-402 |
| T-404 | **Verify frontend image size (<200MB)** | [x] | **Claude Code** | T-403 |
| T-405 | **Test frontend container standalone** | [x] | **Claude Code** | T-404 |
| T-406 | Create backend/.dockerignore | [x] | Claude | None |
| T-407 | Create backend/Dockerfile with multi-stage build | [x] | Claude | T-406 |
| T-408 | **Build backend Docker image** | [x] | **Claude Code** | T-407 |
| T-409 | **Verify backend image size (<300MB)** | [x] | **Claude Code** | T-408 |
| T-410 | **Test backend container standalone** | [x] | **Claude Code** | T-409 |

### Parallel Opportunities (Phase A)
- T-401 and T-406 can run in parallel (no dependencies)
- T-402-T-405 (frontend) and T-407-T-410 (backend) can run in parallel after their respective .dockerignore files

---

## Phase B: Helm Charts & K8s Manifests (T-411 to T-425)

**Objective**: Create complete Helm chart with all Kubernetes resource templates.

**Claude Code Executes**:
- `helm lint ./helm/` (validation)
- `helm template taskflow ./helm/ -f ./helm/values-dev.yaml` (dry-run)

| ID | Task Title | Status | Executor | Dependency |
|----|------------|--------|----------|------------|
| T-411 | Create helm/ directory structure | [x] | Claude | None |
| T-412 | Create helm/Chart.yaml | [x] | Claude | T-411 |
| T-413 | Create helm/values.yaml with defaults | [x] | Claude | T-412 |
| T-414 | Create helm/values-dev.yaml with dev overrides | [x] | Claude | T-413 |
| T-415 | Create helm/templates/_helpers.tpl | [x] | Claude | T-412 |
| T-416 | Create frontend-deployment.yaml template | [x] | Claude | T-415 |
| T-417 | Create frontend-service.yaml template | [x] | Claude | T-416 |
| T-418 | Create backend-deployment.yaml template | [x] | Claude | T-415 |
| T-419 | Create backend-service.yaml template | [x] | Claude | T-418 |
| T-420 | Create configmap.yaml template | [x] | Claude | T-415 |
| T-421 | Create secrets.yaml placeholder template | [x] | Claude | T-415 |
| T-422 | Add health probes to frontend deployment | [x] | Claude | T-416 |
| T-423 | Add health probes to backend deployment | [x] | Claude | T-418 |
| T-424 | Create NOTES.txt with post-install instructions | [x] | Claude | T-417, T-419 |
| T-425 | **Validate Helm chart with helm lint** | [x] | **Claude Code** | T-424 |

### Parallel Opportunities (Phase B)
- T-416/T-417 (frontend) and T-418/T-419 (backend) can run in parallel after T-415
- T-420 and T-421 can run in parallel with deployment templates
- T-422 and T-423 can run in parallel (health probes)

---

## Phase C: Minikube Deployment (T-426 to T-435)

**Objective**: Deploy application to Minikube and verify all services are operational.

**Claude Code Executes**:
- `minikube status` (verify cluster)
- `minikube image load taskflow-frontend:1.0.0`
- `minikube image load taskflow-backend:1.0.0`
- `kubectl create secret generic taskflow-secrets --from-literal=database-url=... --from-literal=better-auth-secret=...` (user provides values)
- `helm upgrade --install taskflow ./helm/ -f ./helm/values-dev.yaml`
- `kubectl get pods -w` (watch pods reach Running)
- `kubectl get services`
- `kubectl logs deployment/taskflow-backend` (debugging if needed)
- `kubectl port-forward svc/taskflow-frontend 3000:80`
- `kubectl port-forward svc/taskflow-backend 8000:8000`

| ID | Task Title | Status | Executor | Dependency |
|----|------------|--------|----------|------------|
| T-426 | **Verify Minikube cluster running** | [x] | **Claude Code** | None |
| T-427 | **Load frontend image into Minikube** | [x] | **Claude Code** | T-405, T-426 |
| T-428 | **Load backend image into Minikube** | [x] | **Claude Code** | T-410, T-426 |
| T-429 | **Create K8s secrets** (user provides values) | [x] | **Claude Code** | T-426 |
| T-430 | **Install Helm chart to Minikube** | [x] | **Claude Code** | T-425, T-427, T-428, T-429 |
| T-431 | **Verify frontend pods reach Running state** | [x] | **Claude Code** | T-430 |
| T-432 | **Verify backend pods reach Running state** | [x] | **Claude Code** | T-430 |
| T-433 | **Setup port-forward to frontend service** | [x] | **Claude Code** | T-431 |
| T-434 | **Setup port-forward to backend service** | [x] | **Claude Code** | T-432 |
| T-435 | **Verify frontend-backend communication** | [x] | **Claude Code** | T-433, T-434 |

### Parallel Opportunities (Phase C)
- T-427, T-428, T-429 can run in parallel after T-426
- T-431 and T-432 can run in parallel after T-430
- T-433 and T-434 can run in parallel after their respective pods are running

---

## Phase D: Testing & Documentation (T-436 to T-437)

**Objective**: Validate feature parity and create deployment documentation.

**User Manual Actions**:
- Open browser to http://localhost:3000
- Test signup, signin, task CRUD, AI chatbot
- Verify all Phase III features work identically

| ID | Task Title | Status | Executor | Dependency |
|----|------------|--------|----------|------------|
| T-436 | **Manual E2E testing** (user opens browser) | [x] | **User** | T-435 |
| T-437 | Write K8S_SETUP.md documentation | [x] | Claude | T-436 |

---

## Detailed Task Definitions

### Phase A: Docker Setup

---

**T-401: Create frontend/.dockerignore**
- [ ] T-401 [P] Create .dockerignore in frontend/
- **Description**: Create frontend/.dockerignore to exclude unnecessary files from Docker build context, reducing build time and image size.
- **Acceptance Criteria**:
  * File created at `frontend/.dockerignore`
  * Excludes `node_modules/` directory
  * Excludes `.next/` build output
  * Excludes `.git/` directory
  * Excludes `.env*` files
  * Excludes `*.md` documentation files
- **References**: [spec.md: FR-407], [contracts/docker-contracts.md]

---

**T-402: Create frontend/Dockerfile with multi-stage build**
- [ ] T-402 Create Dockerfile in frontend/
- **Depends**: T-401
- **Description**: Create frontend/Dockerfile with multi-stage build pattern: builder stage for npm ci and build, runner stage for minimal production image.
- **Acceptance Criteria**:
  * Stage 1 (builder): Uses `node:20-alpine` base image
  * Stage 1: Runs `npm ci` for deterministic deps
  * Stage 1: Runs `npm run build` to generate .next
  * Stage 2 (runner): Uses `node:20-alpine` base image
  * Stage 2: Copies only .next/standalone output from builder
  * Stage 2: Creates non-root user (nextjs:nodejs)
  * Stage 2: `EXPOSE 3000`
  * Stage 2: `CMD ["node", "server.js"]`
  * No hardcoded secrets in any layer
- **References**: [spec.md: FR-401, FR-402, FR-403], [contracts/docker-contracts.md]

---

**T-403: Build frontend Docker image [Claude Code Executes]**
- [ ] T-403 Build taskflow-frontend:1.0.0 image
- **Depends**: T-402
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code executes docker build command to create frontend image and verifies build completes without errors.
- **Acceptance Criteria**:
  * Claude Code runs: `docker build -t taskflow-frontend:1.0.0 ./frontend`
  * Build completes without errors
  * Image appears in `docker images` output
  * Build time under 5 minutes (with cache)
  * No security warnings in build output
- **References**: [spec.md: FR-410, FR-475, SC-401], [plan.md: Phase A]

---

**T-404: Verify frontend image size (<200MB) [Claude Code Executes]**
- [ ] T-404 Verify frontend image size
- **Depends**: T-403
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code checks that the built frontend image meets the <200MB size target.
- **Acceptance Criteria**:
  * Claude Code runs: `docker images taskflow-frontend:1.0.0 --format "{{.Size}}"`
  * Image size is under 200MB
  * If over, Claude Code identifies layers to optimize
  * Claude Code reports actual size
- **References**: [spec.md: FR-408, SC-401], [constitution: Container-First Design]

---

**T-405: Test frontend container standalone [Claude Code Executes]**
- [ ] T-405 Test frontend container runs correctly
- **Depends**: T-404
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code runs frontend container in isolation to verify it starts correctly and serves content on port 3000.
- **Acceptance Criteria**:
  * Claude Code runs: `docker run -d -p 3000:3000 taskflow-frontend:1.0.0`
  * Container starts without errors
  * Claude Code verifies http://localhost:3000 returns HTML
  * Claude Code checks container logs for errors
  * Claude Code stops and removes test container
- **References**: [spec.md: FR-403], [contracts/docker-contracts.md]

---

**T-406: Create backend/.dockerignore**
- [ ] T-406 [P] Create .dockerignore in backend/
- **Description**: Create backend/.dockerignore to exclude unnecessary files from Docker build context.
- **Acceptance Criteria**:
  * File created at `backend/.dockerignore`
  * Excludes `__pycache__/` directories
  * Excludes `.venv/` virtual environment
  * Excludes `.git/` directory
  * Excludes `.env*` files
  * Excludes `*.md` documentation files
  * Excludes `.pytest_cache/` test artifacts
- **References**: [spec.md: FR-407], [contracts/docker-contracts.md]

---

**T-407: Create backend/Dockerfile with multi-stage build**
- [ ] T-407 Create Dockerfile in backend/
- **Depends**: T-406
- **Description**: Create backend/Dockerfile with multi-stage build pattern using Python 3.13-slim base image.
- **Acceptance Criteria**:
  * Stage 1 (builder): Uses `python:3.13-slim` base image
  * Stage 1: Installs build dependencies if needed
  * Stage 1: Copies requirements.txt and runs `pip install`
  * Stage 2 (runner): Uses `python:3.13-slim` base image
  * Stage 2: Copies site-packages from builder
  * Stage 2: Copies application code to `/app`
  * Stage 2: Sets `WORKDIR /app`
  * Stage 2: `EXPOSE 8000`
  * Stage 2: `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`
  * No hardcoded secrets in any layer
- **References**: [spec.md: FR-404, FR-405, FR-406], [contracts/docker-contracts.md]

---

**T-408: Build backend Docker image [Claude Code Executes]**
- [ ] T-408 Build taskflow-backend:1.0.0 image
- **Depends**: T-407
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code executes docker build command to create backend image and verifies build completes without errors.
- **Acceptance Criteria**:
  * Claude Code runs: `docker build -t taskflow-backend:1.0.0 ./backend`
  * Build completes without errors
  * Image appears in `docker images` output
  * Build time under 3 minutes (with cache)
  * All Python dependencies install successfully
- **References**: [spec.md: FR-410, FR-476, SC-402], [plan.md: Phase A]

---

**T-409: Verify backend image size (<300MB) [Claude Code Executes]**
- [ ] T-409 Verify backend image size
- **Depends**: T-408
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code checks that the built backend image meets the <300MB size target.
- **Acceptance Criteria**:
  * Claude Code runs: `docker images taskflow-backend:1.0.0 --format "{{.Size}}"`
  * Image size is under 300MB
  * If over, Claude Code identifies layers to optimize
  * Claude Code reports actual size
- **References**: [spec.md: FR-409, SC-402], [constitution: Container-First Design]

---

**T-410: Test backend container standalone [Claude Code Executes]**
- [ ] T-410 Test backend container runs correctly
- **Depends**: T-409
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code runs backend container in isolation to verify it starts correctly and responds to health checks on port 8000.
- **Acceptance Criteria**:
  * Claude Code runs: `docker run -d -p 8000:8000 -e DATABASE_URL=... -e BETTER_AUTH_SECRET=... taskflow-backend:1.0.0`
  * Container starts without errors
  * Claude Code verifies http://localhost:8000/health returns 200 OK
  * Claude Code checks container logs for startup message
  * Claude Code stops and removes test container
- **References**: [spec.md: FR-406], [contracts/docker-contracts.md]

---

### Phase B: Helm Charts & K8s Manifests

---

**T-411: Create helm/ directory structure**
- [ ] T-411 Create helm/ directory structure
- **Description**: Create the Helm chart directory structure at repository root with templates subdirectory.
- **Acceptance Criteria**:
  * Directory `helm/` created at repository root
  * Subdirectory `helm/templates/` created
  * Structure matches plan.md specification
- **References**: [plan.md: Project Structure], [contracts/helm-contracts.md]

---

**T-412: Create helm/Chart.yaml**
- [ ] T-412 Create Chart.yaml in helm/
- **Depends**: T-411
- **Description**: Create Helm chart metadata file with apiVersion v2, chart name, version, and description.
- **Acceptance Criteria**:
  * File created at `helm/Chart.yaml`
  * `apiVersion: v2` (Helm 3 format)
  * `name: taskflow`
  * `version: 1.0.0`
  * `appVersion: "1.0.0"`
  * `description` field with meaningful text
  * `type: application`
- **References**: [spec.md: FR-439], [contracts/helm-contracts.md]

---

**T-413: Create helm/values.yaml with defaults**
- [ ] T-413 Create values.yaml in helm/
- **Depends**: T-412
- **Description**: Create default values file with replica counts, image configurations, resource limits, and config references.
- **Acceptance Criteria**:
  * File created at `helm/values.yaml`
  * `replicaCount: 2` (default)
  * Frontend image config: `repository: taskflow-frontend`, `tag: "1.0.0"`, `pullPolicy: IfNotPresent`
  * Backend image config: `repository: taskflow-backend`, `tag: "1.0.0"`, `pullPolicy: IfNotPresent`
  * Frontend resources: requests (100m CPU, 128Mi), limits (250m CPU, 256Mi)
  * Backend resources: requests (250m CPU, 256Mi), limits (500m CPU, 512Mi)
  * Config section with frontendUrl, backendUrl, nodeEnv
  * Secrets section with secretName reference (not actual values)
- **References**: [spec.md: FR-440], [contracts/helm-contracts.md], [data-model.md]

---

**T-414: Create helm/values-dev.yaml with dev overrides**
- [ ] T-414 Create values-dev.yaml in helm/
- **Depends**: T-413
- **Description**: Create development-specific overrides for local Minikube deployment.
- **Acceptance Criteria**:
  * File created at `helm/values-dev.yaml`
  * `replicaCount: 1` (single replica for dev)
  * Frontend: `pullPolicy: Never` (use locally loaded images)
  * Backend: `pullPolicy: Never`
  * Config: `nodeEnv: "development"`, `logLevel: "debug"`
- **References**: [spec.md: FR-441], [contracts/helm-contracts.md]

---

**T-415: Create helm/templates/_helpers.tpl**
- [ ] T-415 Create _helpers.tpl in helm/templates/
- **Depends**: T-412
- **Description**: Create template helper functions for generating consistent labels and selectors across all K8s resources.
- **Acceptance Criteria**:
  * File created at `helm/templates/_helpers.tpl`
  * Define `taskflow.labels` helper (app, version, chart labels)
  * Define `taskflow.frontend.labels` helper (includes component: frontend)
  * Define `taskflow.backend.labels` helper (includes component: backend)
  * Define `taskflow.selectorLabels` helper for pod selectors
  * Proper Go template syntax
- **References**: [spec.md: FR-447], [contracts/helm-contracts.md]

---

**T-416: Create frontend-deployment.yaml template**
- [ ] T-416 Create frontend-deployment.yaml in helm/templates/
- **Depends**: T-415
- **Description**: Create Kubernetes Deployment template for frontend with configurable replicas, image, resources, and environment variables.
- **Acceptance Criteria**:
  * File created at `helm/templates/frontend-deployment.yaml`
  * `apiVersion: apps/v1`, `kind: Deployment`
  * Uses `{{ .Values.replicaCount }}` for replicas
  * Uses helpers for labels and selectors
  * Container spec references frontend image from values
  * `containerPort: 3000`
  * Resource requests/limits from values
  * envFrom references ConfigMap
  * `imagePullPolicy` from values
- **References**: [spec.md: FR-411, FR-413, FR-415, FR-416, FR-417, FR-418], [data-model.md]

---

**T-417: Create frontend-service.yaml template**
- [ ] T-417 Create frontend-service.yaml in helm/templates/
- **Depends**: T-416
- **Description**: Create Kubernetes Service template for frontend with ClusterIP type and configurable ports.
- **Acceptance Criteria**:
  * File created at `helm/templates/frontend-service.yaml`
  * `apiVersion: v1`, `kind: Service`
  * `type: ClusterIP` (or NodePort based on values)
  * Selector matches frontend deployment labels
  * `port: 80`, `targetPort: 3000`
  * Uses helpers for consistent naming
- **References**: [spec.md: FR-419, FR-421, FR-422, FR-423], [data-model.md]

---

**T-418: Create backend-deployment.yaml template**
- [ ] T-418 Create backend-deployment.yaml in helm/templates/
- **Depends**: T-415
- **Description**: Create Kubernetes Deployment template for backend with configurable replicas, image, resources, and secret injection.
- **Acceptance Criteria**:
  * File created at `helm/templates/backend-deployment.yaml`
  * `apiVersion: apps/v1`, `kind: Deployment`
  * Uses `{{ .Values.replicaCount }}` for replicas
  * Uses helpers for labels and selectors
  * Container spec references backend image from values
  * `containerPort: 8000`
  * Resource requests/limits from values
  * envFrom references ConfigMap
  * env references Secrets for DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY
  * `imagePullPolicy` from values
- **References**: [spec.md: FR-412, FR-414, FR-415, FR-416, FR-417, FR-418], [data-model.md]

---

**T-419: Create backend-service.yaml template**
- [ ] T-419 Create backend-service.yaml in helm/templates/
- **Depends**: T-418
- **Description**: Create Kubernetes Service template for backend with ClusterIP type for internal access.
- **Acceptance Criteria**:
  * File created at `helm/templates/backend-service.yaml`
  * `apiVersion: v1`, `kind: Service`
  * `type: ClusterIP` (internal only)
  * Selector matches backend deployment labels
  * `port: 8000`, `targetPort: 8000`
  * Uses helpers for consistent naming
- **References**: [spec.md: FR-420, FR-421, FR-422, FR-423], [data-model.md]

---

**T-420: Create configmap.yaml template**
- [ ] T-420 Create configmap.yaml in helm/templates/
- **Depends**: T-415
- **Description**: Create ConfigMap template for non-secret configuration values injected into containers.
- **Acceptance Criteria**:
  * File created at `helm/templates/configmap.yaml`
  * `apiVersion: v1`, `kind: ConfigMap`
  * Name uses chart name (taskflow-config)
  * Data includes: FRONTEND_URL, BACKEND_URL, NODE_ENV, LOG_LEVEL
  * Values reference `{{ .Values.config.* }}`
  * Proper quoting for string values
- **References**: [spec.md: FR-425, FR-427], [data-model.md]

---

**T-421: Create secrets.yaml placeholder template**
- [ ] T-421 Create secrets.yaml in helm/templates/
- **Depends**: T-415
- **Description**: Create Secret template as documentation/placeholder only (real secrets created manually via kubectl).
- **Acceptance Criteria**:
  * File created at `helm/templates/secrets.yaml`
  * Contains comments explaining manual secret creation
  * Template is DISABLED by default (wrapped in `{{- if .Values.secrets.create }}`)
  * Documents expected keys: database-url, better-auth-secret, openai-api-key
  * Includes kubectl command example in comments
- **References**: [spec.md: FR-426, FR-428, FR-430], [contracts/helm-contracts.md]

---

**T-422: Add health probes to frontend deployment**
- [ ] T-422 Add liveness/readiness probes to frontend-deployment.yaml
- **Depends**: T-416
- **Description**: Add liveness and readiness probe configurations to frontend deployment for Kubernetes health monitoring.
- **Acceptance Criteria**:
  * Liveness probe: TCP socket on port 3000
  * Liveness: `initialDelaySeconds: 30`, `periodSeconds: 10`, `failureThreshold: 3`
  * Readiness probe: TCP socket on port 3000
  * Readiness: `initialDelaySeconds: 10`, `periodSeconds: 5`, `failureThreshold: 3`
  * Both probes configurable via values.yaml
- **References**: [spec.md: FR-433, FR-434, FR-437, FR-438], [research.md: Health Checks]

---

**T-423: Add health probes to backend deployment**
- [ ] T-423 Add liveness/readiness probes to backend-deployment.yaml
- **Depends**: T-418
- **Description**: Add liveness and readiness probe configurations to backend deployment for Kubernetes health monitoring.
- **Acceptance Criteria**:
  * Liveness probe: HTTP GET `/health` on port 8000
  * Liveness: `initialDelaySeconds: 30`, `periodSeconds: 10`, `failureThreshold: 3`
  * Readiness probe: HTTP GET `/health` on port 8000
  * Readiness: `initialDelaySeconds: 10`, `periodSeconds: 5`, `failureThreshold: 3`
  * Both probes configurable via values.yaml
- **References**: [spec.md: FR-431, FR-432, FR-437, FR-438], [research.md: Health Checks]

---

**T-424: Create NOTES.txt with post-install instructions**
- [ ] T-424 Create NOTES.txt in helm/templates/
- **Depends**: T-417, T-419
- **Description**: Create Helm NOTES.txt that displays helpful post-installation instructions including port-forward commands.
- **Acceptance Criteria**:
  * File created at `helm/templates/NOTES.txt`
  * Shows release name and namespace
  * Provides port-forward commands for frontend and backend
  * Includes verification steps (kubectl get pods, kubectl get svc)
  * Shows URLs for accessing the application
  * Includes troubleshooting tips
- **References**: [spec.md: FR-446], [contracts/helm-contracts.md]

---

**T-425: Validate Helm chart with helm lint [Claude Code Executes]**
- [ ] T-425 Run helm lint and fix any errors
- **Depends**: T-424
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code runs Helm linting to validate chart syntax and structure, fixing any reported errors.
- **Acceptance Criteria**:
  * Claude Code runs: `helm lint ./helm/`
  * Zero errors reported
  * Zero critical warnings
  * Claude Code runs: `helm template taskflow ./helm/ -f ./helm/values-dev.yaml` renders valid YAML
  * All template files render without Go template errors
- **References**: [spec.md: FR-448, FR-480, SC-403], [plan.md: Success Validation]

---

### Phase C: Minikube Deployment

---

**T-426: Verify Minikube cluster running [Claude Code Executes]**
- [ ] T-426 Verify Minikube cluster is running
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code verifies Minikube cluster is running (user should have started it once before session).
- **Acceptance Criteria**:
  * Claude Code runs: `minikube status`
  * Cluster shows "Running" status
  * Claude Code runs: `kubectl cluster-info` shows running control plane
  * Claude Code runs: `kubectl get nodes` shows Ready node
  * If not running, Claude Code prompts user to run: `minikube start --memory=4096 --cpus=2`
- **References**: [quickstart.md: Step 1], [spec.md: Assumptions]

---

**T-427: Load frontend image into Minikube [Claude Code Executes]**
- [ ] T-427 [P] Load frontend image to Minikube
- **Depends**: T-405, T-426
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code loads the locally built frontend Docker image into Minikube's image cache.
- **Acceptance Criteria**:
  * Claude Code runs: `minikube image load taskflow-frontend:1.0.0`
  * Command completes without errors
  * Claude Code verifies: `minikube image ls | grep taskflow-frontend` shows image
  * Image available for pods with `imagePullPolicy: Never`
- **References**: [spec.md: FR-477, US-1 Scenario 2], [quickstart.md: Step 3]

---

**T-428: Load backend image into Minikube [Claude Code Executes]**
- [ ] T-428 [P] Load backend image to Minikube
- **Depends**: T-410, T-426
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code loads the locally built backend Docker image into Minikube's image cache.
- **Acceptance Criteria**:
  * Claude Code runs: `minikube image load taskflow-backend:1.0.0`
  * Command completes without errors
  * Claude Code verifies: `minikube image ls | grep taskflow-backend` shows image
  * Image available for pods with `imagePullPolicy: Never`
- **References**: [spec.md: FR-478, US-2 Scenario 2], [quickstart.md: Step 3]

---

**T-429: Create K8s secrets [Claude Code Executes, User Provides Values]**
- [ ] T-429 [P] Create taskflow-secrets in Kubernetes
- **Depends**: T-426
- **Executor**: **Claude Code** (automated, user provides secret values)
- **Description**: Claude Code creates Kubernetes Secret. User provides DATABASE_URL, BETTER_AUTH_SECRET, and OPENAI_API_KEY values when prompted.
- **Acceptance Criteria**:
  * Claude Code prompts user for secret values
  * Claude Code runs: `kubectl create secret generic taskflow-secrets --from-literal=database-url=<user-value> --from-literal=better-auth-secret=<user-value> --from-literal=openai-api-key=<user-value>`
  * Secret created successfully
  * Claude Code verifies: `kubectl get secret taskflow-secrets` shows Opaque type with 3 data items
  * Actual credential values NOT committed to any file
- **References**: [spec.md: FR-426, FR-479, FR-464], [quickstart.md: Step 4]

---

**T-430: Install Helm chart to Minikube [Claude Code Executes]**
- [ ] T-430 Deploy TaskFlow with Helm
- **Depends**: T-425, T-427, T-428, T-429
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code installs the TaskFlow Helm chart to Minikube using development values file.
- **Acceptance Criteria**:
  * Claude Code runs: `helm upgrade --install taskflow ./helm/ -f ./helm/values-dev.yaml`
  * Installation completes without errors
  * NOTES.txt output displays correctly
  * Claude Code verifies: `kubectl get all -l app=taskflow` shows deployments, pods, services
  * Claude Code verifies: `kubectl get cm taskflow-config` shows ConfigMap created
- **References**: [spec.md: FR-449, FR-450, FR-481, SC-404], [quickstart.md: Step 5]

---

**T-431: Verify frontend pods reach Running state [Claude Code Executes]**
- [ ] T-431 [P] Verify frontend pods are Running
- **Depends**: T-430
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code verifies that frontend pods start successfully and reach Running state within 30 seconds.
- **Acceptance Criteria**:
  * Claude Code runs: `kubectl get pods -l app=taskflow,component=frontend`
  * Pod status is `Running` (not Pending, CrashLoopBackOff, etc.)
  * Pod reaches Running within 30 seconds
  * Claude Code runs: `kubectl describe pod` if issues found
  * Container ready (1/1)
- **References**: [spec.md: FR-451, FR-482, SC-405], [spec.md: US-1 Scenario 3]

---

**T-432: Verify backend pods reach Running state [Claude Code Executes]**
- [ ] T-432 [P] Verify backend pods are Running
- **Depends**: T-430
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code verifies that backend pods start successfully and reach Running state within 30 seconds.
- **Acceptance Criteria**:
  * Claude Code runs: `kubectl get pods -l app=taskflow,component=backend`
  * Pod status is `Running`
  * Pod reaches Running within 30 seconds
  * Claude Code runs: `kubectl logs` to check for errors if needed
  * Container ready (1/1)
  * Liveness/readiness probes passing
- **References**: [spec.md: FR-452, FR-482, SC-406], [spec.md: US-2 Scenario 3]

---

**T-433: Setup port-forward to frontend service [Claude Code Executes]**
- [ ] T-433 [P] Port-forward frontend and verify access
- **Depends**: T-431
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code sets up port forwarding to frontend service and verifies application is accessible at localhost:3000.
- **Acceptance Criteria**:
  * Claude Code runs: `kubectl port-forward svc/taskflow-frontend 3000:80` (in background)
  * Port-forward establishes successfully
  * Claude Code verifies http://localhost:3000 returns HTML status 200
  * Login page displays correctly
  * Port-forward remains active for user testing
- **References**: [spec.md: FR-465, FR-484, SC-407], [spec.md: US-4 Scenario 1]

---

**T-434: Setup port-forward to backend service [Claude Code Executes]**
- [ ] T-434 [P] Port-forward backend and verify access
- **Depends**: T-432
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code sets up port forwarding to backend service and verifies API is accessible at localhost:8000.
- **Acceptance Criteria**:
  * Claude Code runs: `kubectl port-forward svc/taskflow-backend 8000:8000` (in background)
  * Port-forward establishes successfully
  * Claude Code verifies http://localhost:8000/health returns 200 OK
  * Claude Code verifies http://localhost:8000/docs returns Swagger UI
  * Claude Code checks logs for database connection success
- **References**: [spec.md: FR-466, FR-485, SC-408], [spec.md: US-2 Scenario 4]

---

**T-435: Verify frontend-backend communication [Claude Code Executes]**
- [ ] T-435 Test service-to-service communication
- **Depends**: T-433, T-434
- **Executor**: **Claude Code** (automated)
- **Description**: Claude Code verifies that frontend can communicate with backend via Kubernetes service DNS.
- **Acceptance Criteria**:
  * With both port-forwards active, Claude Code verifies http://localhost:3000 accessible
  * Claude Code checks backend logs for incoming requests
  * Claude Code verifies backend service is accessible at `taskflow-backend:8000` from within cluster
  * Claude Code notifies user that manual browser testing is ready
- **References**: [spec.md: FR-423, SC-409, SC-410, SC-411], [spec.md: US-3]

---

### Phase D: Testing & Documentation

---

**T-436: Manual E2E testing of all Phase III features [USER TESTS]**
- [ ] T-436 Complete E2E testing of all features in K8s
- **Depends**: T-435
- **Executor**: **USER** (manual browser testing)
- **Description**: **USER** manually tests all Phase III features in browser to verify feature parity in the Kubernetes environment.
- **User Actions**:
  * Open browser to http://localhost:3000
  * **Signup**: Create new user account → success
  * **Signin**: Login with created account → success, JWT works
  * **Task CRUD**: Create, read, update, delete tasks → all operations work
  * **Task Toggle**: Mark tasks complete/incomplete → persists correctly
  * **Chatbot**: AI chatbot responds correctly (if OpenAI key configured)
  * Confirm no feature regressions from Phase III local deployment
- **References**: [spec.md: FR-469-474, SC-410-416, SC-418-423], [spec.md: US-4, US-5]

---

**T-437: Write K8S_SETUP.md documentation**
- [ ] T-437 Create K8S_SETUP.md at repository root
- **Depends**: T-436
- **Description**: Create comprehensive deployment documentation for developers to deploy TaskFlow to Minikube.
- **Acceptance Criteria**:
  * File created at `K8S_SETUP.md` (repository root)
  * **Prerequisites**: Lists required tools (Docker, Minikube, kubectl, Helm) with version requirements
  * **Quick Start**: Step-by-step commands from zero to running app
  * **Build Images**: Docker build commands for frontend and backend
  * **Create Secrets**: Instructions for manual secret creation (with placeholders)
  * **Deploy**: Helm install command with values-dev.yaml
  * **Access**: Port-forward commands and URLs
  * **Verify**: Commands to check pod status, logs, services
  * **Troubleshooting**: Common issues and solutions
  * **Cleanup**: Helm uninstall and Minikube stop commands
  * Developer can follow instructions and successfully deploy without external help
- **References**: [spec.md: SC-429, NFR: Documentation Clarity], [quickstart.md]

---

## Dependency Graph

```
Phase A (Docker):
  T-401 ─┬─► T-402 ─► T-403 ─► T-404 ─► T-405 ──────────────┐
         │                                                    │
  T-406 ─┴─► T-407 ─► T-408 ─► T-409 ─► T-410 ──────────────┤
                                                              │
Phase B (Helm):                                               │
  T-411 ─► T-412 ─┬─► T-413 ─► T-414                         │
                  │                                           │
                  └─► T-415 ─┬─► T-416 ─► T-417 ─┐           │
                             │                   │           │
                             ├─► T-418 ─► T-419 ─┼─► T-424   │
                             │                   │     │     │
                             ├─► T-420           │     │     │
                             │                   │     │     │
                             └─► T-421           │     │     │
                                                 │     │     │
                             T-422 ◄─────────────┘     │     │
                             T-423 ◄───────────────────┘     │
                                                       │     │
                                        T-425 ◄────────┘     │
                                          │                  │
Phase C (Deployment):                     │                  │
  T-426 ─┬─► T-427 ◄─────────────────────────────────────────┘
         │                                │
         ├─► T-428 ◄──────────────────────┤
         │                                │
         └─► T-429                        │
               │                          │
               └─────► T-430 ◄────────────┘
                         │
                    ┌────┴────┐
                    ▼         ▼
                 T-431     T-432
                    │         │
                    ▼         ▼
                 T-433     T-434
                    │         │
                    └────┬────┘
                         ▼
                      T-435
                         │
Phase D (Testing):       │
                         ▼
                      T-436
                         │
                         ▼
                      T-437
```

---

## Parallel Execution Opportunities

### Phase A Parallelization
```bash
# Run in parallel (2 tracks)
Track 1: T-401 → T-402 → T-403 → T-404 → T-405 (Frontend)
Track 2: T-406 → T-407 → T-408 → T-409 → T-410 (Backend)
```

### Phase B Parallelization
```bash
# After T-415 completes, run in parallel (3 tracks)
Track 1: T-416 → T-417 → T-422 (Frontend deployment/service/probes)
Track 2: T-418 → T-419 → T-423 (Backend deployment/service/probes)
Track 3: T-420, T-421 (ConfigMap, Secrets template)
# Then: T-424 → T-425
```

### Phase C Parallelization
```bash
# After T-426 completes, run in parallel
T-427, T-428, T-429 (all depend only on T-426)
# After T-430 completes
T-431, T-432 (in parallel)
# After pods verified
T-433, T-434 (in parallel)
```

---

## Implementation Strategy

### MVP Scope (Recommended First Pass)
1. Complete Phase A (Docker images working standalone)
2. Complete Phase B through T-425 (Helm chart validated)
3. Complete Phase C through T-435 (App deployed and communicating)
4. Phase D as documentation/polish

### Incremental Delivery Checkpoints
- **Checkpoint 1**: Frontend Docker image builds and runs (T-405)
- **Checkpoint 2**: Backend Docker image builds and runs (T-410)
- **Checkpoint 3**: Helm chart passes lint (T-425)
- **Checkpoint 4**: App deployed to Minikube (T-430)
- **Checkpoint 5**: Full E2E verification (T-436)
- **Final**: Documentation complete (T-437)

---

## References

- **Specification**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Research Decisions**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Docker Contracts**: [contracts/docker-contracts.md](./contracts/docker-contracts.md)
- **Helm Contracts**: [contracts/helm-contracts.md](./contracts/helm-contracts.md)
- **Quickstart Guide**: [quickstart.md](./quickstart.md)
- **Constitution**: [../../.specify/memory/constitution.md](../../.specify/memory/constitution.md)
