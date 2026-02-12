<!--
  SYNC IMPACT REPORT - Phase IV Constitution Amendment
  Version: 3.0.0 → 3.1.0 (MINOR bump: added Command Automation principle XVII)
  Date: 2026-02-08

  Previous Version (3.0.0) Changes:
  - Added Principles XIII-XVI: K8s-Specific governance (Container-First Design, Kubernetes-Native Patterns, Infrastructure as Code, Helm Standards)
  - Extended Technology Stack: Minikube, Docker, Helm, kubectl
  - Extended Architectural Constraints: Container requirements, stateless design, resource management
  - Added Coding Standards: Dockerfile standards, Helm chart standards, K8s manifest standards
  - Extended Security Rules: K8s secrets management, container security, image versioning
  - Added Performance Expectations: Pod startup, deployment rollout, resource efficiency
  - Added Testing Requirements: Dockerfile validation, image size limits, Helm lint, K8s deployment verification
  - Added Non-Negotiables: Container and K8s specific requirements
  - Added Deployment Standards (Phase IV): Local Kubernetes deployment via Minikube

  Current Version (3.1.0) Changes:
  - Added Principle XVII: Command Automation - Claude Code executes all infrastructure commands
  - Clarified automation expectations for docker build, helm install, kubectl operations
  - Added Command Automation Standards section

  Templates Requiring Updates:
  - .specify/templates/plan-template.md: Add K8s infrastructure section (⚠ pending)
  - .specify/templates/spec-template.md: Add container/deployment requirements section (⚠ pending)
  - .specify/templates/tasks-template.md: Add "Infrastructure/K8s" task category (⚠ pending)
  - README.md: Add Phase IV local deployment instructions (⚠ pending)

  Deferred Items: None
-->

# Full-Stack Todo Application Constitution - Phase IV Extension

<!-- Phase II: Production-Ready Multi-User Web Application -->
<!-- Phase III: AI-Powered Conversational Interface with MCP Integration -->
<!-- Phase IV: Local Kubernetes Deployment on Minikube -->

## Core Principles

### I. Security First (NON-NEGOTIABLE)
- **Authentication Required**: All task operations and chat interactions require valid JWT authentication
- **User Isolation Enforced**: Users can only access their own data and conversations; backend validates user_id from JWT matches path user_id on every request
- **Zero Trust**: All inputs validated at API boundary (frontend AND backend); SQL injection prevented via ORM; XSS prevented via React escaping
- **Secrets Management**: All secrets in environment variables (.env files for dev); K8s Secrets for deployment; Never hardcoded; .gitignore excludes all .env files
- **Password Security**: All passwords hashed via bcrypt (Better Auth handles); No passwords in logs; JWT tokens in httpOnly cookies only
- **CORS Configured**: Allow specific frontend origin only; credentials enabled; proper methods and headers whitelisted

### II. Type Safety Mandatory
- **Frontend TypeScript Strict Mode**: No 'any' types unless absolutely necessary; All props, functions, API responses typed; Exhaustive type checking
- **Backend Python Type Hints**: All function parameters and returns typed; Pydantic models for all request/response validation
- **Database Type Safety**: SQLModel ORM combines SQLAlchemy + Pydantic; No raw SQL queries; Type-safe queries throughout

### III. API-First Architecture
- **Clean Separation**: Frontend (Next.js) and backend (FastAPI) are independent services; communicate via REST API only
- **Stateless Backend**: JWT-based authentication; no server sessions; horizontal scaling ready
- **RESTful Conventions**: GET (read), POST (create), PUT (update), DELETE (delete), PATCH (partial); Consistent endpoint structure: /api/{user_id}/{resource}
- **Proper HTTP Status Codes**: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity, 500 Internal Server Error
- **Consistent Response Format**: JSON always; Success returns resource/list; Error returns {"detail": "message"}

### IV. Modern Frontend Standards (Next.js 16+)
- **App Router Only**: File-based routing in app/ directory; Server Components by default; Client Components only when needed ('use client' directive)
- **Tailwind CSS Only**: Utility classes exclusively; No custom CSS files; No inline styles (except dynamic values); Mobile-first responsive design
- **Component Architecture**: Reusable UI in components/ui/; Feature components in components/[feature]/; Single responsibility per component
- **State Management**: React hooks for local state; Server Components for server state; No global state library in Phase 2
- **Centralized API Client**: All backend calls through lib/api.ts; Consistent error handling; Loading states for all async operations

### V. Database Best Practices (SQLModel + PostgreSQL)
- **ORM Required**: SQLModel for all database operations; No raw SQL queries allowed
- **Schema Design**: Normalized tables; Clear foreign key relationships; NOT NULL constraints where appropriate; Unique constraints for natural keys (email); Indexes on frequently queried fields (user_id, conversation_id)
- **Data Integrity**: Foreign key constraints enforced; Validation in application layer (SQLModel + Pydantic); Transactions for multi-step operations; Cascade deletes where appropriate (user deleted → tasks/conversations deleted)
- **Connection Management**: Neon Serverless PostgreSQL; Connection pooling enabled; pool_pre_ping=True for health checks; Connection string from environment variable (or K8s Secret in deployment)

### VI. Authentication & JWT Flow (Better Auth)
- **Better Auth Library**: JWT plugin enabled; Token expiration: 7 days (configurable); Secure password hashing (bcrypt); Email validation
- **JWT Token Flow**: Better Auth issues JWT on login → Stored in httpOnly cookies → Sent in Authorization: Bearer <token> header → Backend verifies JWT signature with shared secret → Extract user_id from token payload (sub claim) → Validate user_id in URL matches token user_id
- **Shared Secret**: BETTER_AUTH_SECRET environment variable (K8s Secret in deployment); Same secret in frontend and backend; Minimum 32 characters; Random, cryptographically secure; Never hardcoded

### VII. Error Handling Philosophy
- **Frontend Error Strategy**: Network errors: helpful message; 401 errors: redirect to login; 404: resource not found; 422: inline validation messages; 500: generic error; Toast notifications for success/error feedback; Loading states prevent duplicate submissions
- **Backend Error Strategy**: HTTPException for expected errors with proper status codes; Descriptive error messages; Exception handlers for unexpected errors; Never expose internal errors/stack traces to client; Log all errors for debugging

### VIII. Code Quality Standards
- **General Principles**: DRY (Don't Repeat Yourself); KISS (Keep It Simple, Stupid); Single Responsibility Principle; Consistent naming conventions; Self-documenting code
- **Avoid Over-Engineering**: Only make changes directly requested or clearly necessary; Keep solutions simple and focused; No premature abstractions; Don't add features, refactoring, or "improvements" beyond what was asked
- **No Unnecessary Comments**: Don't add docstrings, comments, or type annotations to code you didn't change; Only add comments where logic isn't self-evident; Code should be self-documenting via clear naming

### IX. Stateless Chat Architecture (Phase III)
- **No Server-Side Session Memory**: Chat endpoint does not maintain user conversation state between requests
- **Conversation History in Database**: All conversation history stored in Conversation and Message tables; Each request includes full context needed for agent decision-making
- **Agent is Ephemeral**: OpenAI Agent SDK instantiated fresh for each chat request; No persistent agent state across requests
- **Context Passing**: User message + conversation history retrieved from DB → passed to agent → agent executes MCP tools → response stored in DB → returned to client

### X. MCP as Single Source of Truth (Phase III)
- **No Direct Database Access from Chat**: Chat endpoint cannot query database directly; all data access MUST go through MCP tools
- **MCP Tools are Gatekeepers**: Tasks, conversations, and user data accessed only via MCP tools; agent invokes tools, tools verify permissions, tools perform DB operations
- **Tool Execution Isolation**: Each MCP tool execution is independent; tools verify user_id before every operation; tools handle all Pydantic validation and error handling
- **Tool Response Logging**: Every tool invocation logged with user_id, timestamp, tool name, input, and result; enables auditing and debugging

### XI. Agent Intent Routing (Phase III)
- **OpenAI Agent SDK**: Structured reasoning determines whether message requires task action or pure conversation
- **Intent Types**: Create task, read tasks, update task, delete task, toggle task, chat/clarify
- **Tool Selection Discipline**: Agent uses minimal tool set for current intent; no speculative tool calls; agent reasons about next step based on tool results
- **Error Recovery**: Agent retries tool calls with adjusted parameters on recoverable errors; escalates to user with clear explanation on persistent failures

### XII. Conversation Persistence (Phase III)
- **Immutable Message History**: Each user message and agent response stored as Message records; never deleted (soft delete only if audit required)
- **Thread Integrity**: Conversation records group related messages; clear relationship between conversations and tasks mentioned
- **Search & Recall**: Conversation history indexed for user to review past interactions; enables multi-turn context retention without server session

### XIII. Container-First Design (Phase IV)
- **All Components Containerized**: Frontend and Backend MUST run in Docker containers; No bare-metal dependencies in deployment
- **Multi-Stage Builds Required**: Dockerfiles MUST use multi-stage builds for optimization; Build stage separate from runtime stage
- **Minimal Base Images**: Use alpine or slim variants (node:20-alpine, python:3.13-slim); No full OS images
- **No Hardcoded Configuration**: All configuration externalized via environment variables; Containers are environment-agnostic
- **Stateless Containers**: No local file storage; All persistent data in external Neon database; Containers can be killed and recreated without data loss

### XIV. Kubernetes-Native Patterns (Phase IV)
- **Deployments Over Pods**: Always use Deployment resources (not standalone Pods); Enables rolling updates and replica management
- **Services for Networking**: Frontend and Backend exposed via K8s Services; ClusterIP for internal, NodePort/LoadBalancer for external access
- **ConfigMaps for Non-Secret Config**: API URLs, feature flags, non-sensitive settings in ConfigMaps
- **Secrets for Sensitive Data**: DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY MUST be K8s Secrets; Never in ConfigMaps or Helm values
- **Health Checks Required**: Liveness and Readiness probes defined for all containers; Prevents traffic to unhealthy pods
- **Resource Management**: CPU/Memory requests and limits MUST be defined; Prevents resource starvation and enables proper scheduling

### XV. Infrastructure as Code (Phase IV)
- **Declarative Configuration**: All K8s resources defined in version-controlled files; No imperative kubectl create/run commands in production workflow
- **Reproducible Deployments**: Same manifests produce identical deployments; Environment differences handled via values files
- **GitOps Ready**: Infrastructure changes go through same PR review as application code; Audit trail for all deployment changes
- **Idempotent Operations**: helm upgrade --install pattern; Applying same config twice has no side effects

### XVI. Helm Standards (Phase IV)
- **Helm as Package Manager**: All K8s resources defined in Helm charts; No raw kubectl apply on individual YAML files
- **Values-Driven Configuration**: All customizable settings in values.yaml; Environment overrides in values-dev.yaml, values-prod.yaml
- **Templated Manifests**: Use Helm templating for DRY configurations; {{ .Values.* }} for all configurable fields
- **Chart Structure**: Follow standard Helm chart layout (Chart.yaml, values.yaml, templates/)
- **Dependency Management**: External charts referenced in Chart.yaml dependencies; Version-pinned dependencies

### XVII. Command Automation (Phase IV)
- **AI-Executed Infrastructure**: Claude Code executes ALL infrastructure commands (docker build, helm install, kubectl, minikube)
- **No Manual Command Entry**: User MUST NOT need to copy-paste commands; Claude Code runs them directly
- **Scripted Operations**: Common operations wrapped in reusable patterns for consistent execution
- **Error Handling**: Claude Code handles command failures, diagnoses issues, and retries or escalates appropriately
- **Progress Reporting**: Clear feedback to user on command status (building, deploying, verifying)
- **Idempotent Execution**: Commands designed to be safe to re-run without side effects

## Technology Stack

### Frontend Stack
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth (client)
- **State**: React hooks (useState, useEffect, useCallback, useMemo)
- **HTTP Client**: Fetch API (built-in)
- **Chat UI Kit**: OpenAI ChatKit (TypeScript)
- **Container**: Docker (node:20-alpine base)
- **Deployment**: Kubernetes (Minikube local), Vercel (cloud)

### Backend Stack
- **Framework**: FastAPI (async/await)
- **Language**: Python 3.13+ (type hints)
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless - external to K8s)
- **Authentication**: JWT verification (shared secret with Better Auth)
- **Validation**: Pydantic models
- **AI Agent Framework**: OpenAI Agents SDK (Python)
- **MCP Protocol**: Model Context Protocol (server-side MCP implementation)
- **LLM**: OpenAI API (gpt-4o or latest reasoning model)
- **Container**: Docker (python:3.13-slim base)
- **Deployment**: Kubernetes (Minikube local), Railway/Render/Fly.io (cloud)

### Infrastructure Stack (Phase IV)
- **Container Runtime**: Docker Desktop
- **Local Kubernetes**: Minikube
- **Package Manager**: Helm 3
- **CLI Tools**: kubectl, docker, helm, minikube
- **External Database**: Neon PostgreSQL (not containerized)

### Development Tools
- **Package Managers**: npm (frontend), pip/uv (backend)
- **Environment Files**: .env.local (frontend dev), .env (backend dev)
- **Version Control**: Git + GitHub
- **Code Organization**: Separate frontend/ and backend/ folders
- **Infrastructure Code**: k8s/ or helm/ folder at repository root

## Architectural Constraints (Phase IV)

### Container Requirements
- **Frontend Container**: Node.js 20 alpine, standalone Next.js build, <200MB image size
- **Backend Container**: Python 3.13 slim, uvicorn ASGI server, <300MB image size
- **No Local Dependencies**: Containers MUST NOT depend on host machine binaries or paths
- **Port Standardization**: Frontend: 3000 (internal), Backend: 8000 (internal)

### Kubernetes Design
- **Namespace Isolation**: All TaskFlow resources in dedicated namespace (taskflow)
- **Label Consistency**: All resources labeled with `app: taskflow`, `component: frontend|backend`
- **Selector Alignment**: Deployment selectors MUST match Pod template labels
- **Service Discovery**: Backend accessed via service name (taskflow-backend:8000), not IP addresses

### Resource Boundaries
- **Frontend Deployment**: 1-3 replicas, 128Mi-256Mi memory, 100m-250m CPU
- **Backend Deployment**: 1-3 replicas, 256Mi-512Mi memory, 250m-500m CPU
- **Startup Tolerance**: Containers MUST start within 30 seconds
- **Graceful Shutdown**: Containers MUST handle SIGTERM for clean shutdown

### External Dependencies
- **Database**: Neon PostgreSQL remains external; accessed via DATABASE_URL secret
- **OpenAI API**: Accessed via OPENAI_API_KEY secret; no local LLM
- **No In-Cluster Database**: PostgreSQL NOT deployed in Minikube (Neon handles this)

## Coding Standards (Phase IV Extensions)

### Dockerfile Standards
```dockerfile
# REQUIRED: Multi-stage build pattern
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine AS runner
WORKDIR /app
# REQUIRED: Non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

**Rules**:
- MUST use multi-stage builds
- MUST use specific version tags (node:20-alpine, NOT node:alpine or node:latest)
- MUST run as non-root user
- MUST NOT contain secrets or passwords
- MUST NOT use ADD for remote URLs (use COPY)
- MUST minimize layer count (combine RUN commands where logical)

### Helm Chart Standards
```yaml
# values.yaml structure
replicaCount: 1

image:
  repository: taskflow-frontend
  tag: "1.0.0"  # MUST be specific version
  pullPolicy: IfNotPresent

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "250m"

# Secrets referenced, NOT stored
secrets:
  # Values injected at runtime, not in this file
  databaseUrlSecretName: taskflow-secrets
  betterAuthSecretName: taskflow-secrets
```

**Rules**:
- MUST use templating for all configurable values
- MUST NOT hardcode secrets in values.yaml
- MUST define resource requests AND limits
- MUST use specific image tags (never :latest)
- MUST pass `helm lint` without errors

### Kubernetes Manifest Standards
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskflow-backend
  labels:
    app: taskflow          # REQUIRED: App label
    component: backend     # REQUIRED: Component label
spec:
  replicas: 1
  selector:
    matchLabels:
      app: taskflow
      component: backend   # MUST match template labels
  template:
    metadata:
      labels:
        app: taskflow
        component: backend
    spec:
      containers:
      - name: backend
        image: taskflow-backend:1.0.0  # Specific version
        ports:
        - containerPort: 8000
        resources:                      # REQUIRED
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:              # Secrets from K8s Secrets
              name: taskflow-secrets
              key: database-url
```

**Rules**:
- MUST include app and component labels on all resources
- MUST define resource requests and limits
- MUST use secretKeyRef for sensitive environment variables
- MUST NOT use :latest image tags
- MUST have matching selectors and template labels

## Command Automation Standards (Phase IV)

### Automated Command Categories
- **Container Commands**: `docker build`, `docker tag`, `docker images`, `docker inspect`
- **Minikube Commands**: `minikube start`, `minikube status`, `minikube image load`, `minikube service`
- **Helm Commands**: `helm lint`, `helm template`, `helm upgrade --install`, `helm list`, `helm uninstall`
- **Kubectl Commands**: `kubectl apply`, `kubectl get`, `kubectl describe`, `kubectl logs`, `kubectl create secret`
- **Verification Commands**: `kubectl get pods`, `kubectl get services`, health check endpoints

### Execution Patterns
```bash
# Pattern 1: Sequential with verification
docker build -t taskflow-frontend:1.0.0 ./frontend && \
minikube image load taskflow-frontend:1.0.0 && \
kubectl get pods | grep frontend

# Pattern 2: Helm deployment with status check
helm upgrade --install taskflow ./charts/taskflow -f values-dev.yaml && \
kubectl rollout status deployment/taskflow-frontend && \
kubectl rollout status deployment/taskflow-backend

# Pattern 3: Port-forward for user testing (runs in background)
kubectl port-forward svc/taskflow-frontend 3000:3000
```

### Command Output Handling
- **Success**: Report completion, show relevant output (pod status, service URLs)
- **Failure**: Diagnose error, suggest fix, retry if appropriate
- **Long-Running**: Inform user of progress, use `--wait` flags where available
- **Interactive**: NEVER use interactive flags (-i, --interactive); all commands must be non-interactive

### User Involvement
- **Secrets Only**: User provides secret values (DATABASE_URL, API keys) verbally or via secure input
- **Browser Testing**: User manually tests via `localhost:3000` after port-forward
- **Approval Gates**: User confirms before destructive operations (delete, uninstall)

## Security Rules (Phase IV)

### Secrets Management
- **K8s Secrets for All Sensitive Data**: DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY
- **Manual Secret Creation**: `kubectl create secret generic taskflow-secrets --from-literal=database-url=... --from-literal=better-auth-secret=...`
- **No Secrets in Git**: Secrets NEVER committed to repository; create manually or via sealed-secrets
- **No Secrets in Dockerfiles**: Build args for secrets are forbidden
- **No Secrets in Helm Values**: values.yaml references secret names, not secret values

### Container Security
- **Non-Root Execution**: All containers MUST run as non-root user
- **Read-Only Filesystem**: Where possible, use readOnlyRootFilesystem: true
- **No Privilege Escalation**: allowPrivilegeEscalation: false
- **Specific Base Images**: Pin to exact versions (node:20-alpine, NOT node:20)
- **Minimal Attack Surface**: Only install required packages; no dev dependencies in runtime image

### Network Security
- **Internal Services**: Backend service not exposed externally (ClusterIP)
- **Frontend Ingress**: Only frontend exposed via NodePort or Ingress
- **Inter-Service Auth**: Backend validates JWT on every request (same as Phase II/III)

## Performance Expectations (Phase IV)

### Container Performance
- **Image Build Time**: <5 minutes per image (with cache)
- **Image Size**: Frontend <200MB, Backend <300MB
- **Container Startup**: <30 seconds to healthy state

### Kubernetes Performance
- **Pod Startup Time**: <30 seconds per pod (from scheduled to ready)
- **Deployment Rollout**: <2 minutes for all replicas to reach Ready state
- **Service Availability**: Zero downtime during rolling updates

### Resource Efficiency
- **Frontend Pod**: <256MB memory at steady state
- **Backend Pod**: <512MB memory at steady state
- **CPU Utilization**: <50% at idle, scales with load

### Scaling
- **Horizontal Scaling**: Support 2-3 replicas per deployment without issues
- **Load Distribution**: Traffic evenly distributed across replicas via Service
- **Database Connections**: Connection pooling handles multiple backend replicas

## Testing Requirements (Phase IV)

### Dockerfile Validation
- [ ] `docker build` completes without errors
- [ ] Multi-stage build produces minimal runtime image
- [ ] Image runs without root privileges
- [ ] No secrets baked into image layers
- [ ] Image starts and responds to health checks

### Docker Image Requirements
- [ ] Frontend image <200MB
- [ ] Backend image <300MB
- [ ] Images tagged with semantic versions (not :latest)
- [ ] Images load successfully into Minikube (`minikube image load`)

### Helm Chart Validation
- [ ] `helm lint charts/taskflow` passes without errors
- [ ] `helm template` renders valid YAML
- [ ] All values documented in values.yaml
- [ ] Environment-specific overrides work (values-dev.yaml)

### Kubernetes Deployment Testing
- [ ] `kubectl apply` creates all resources without errors
- [ ] Pods reach Running state within 30 seconds
- [ ] Services route traffic correctly
- [ ] Secrets injected as environment variables
- [ ] Health checks pass (liveness/readiness probes)
- [ ] Application functions correctly in K8s environment
- [ ] Frontend can communicate with backend via service name
- [ ] Backend can connect to external Neon database

### End-to-End K8s Tests
- [ ] Fresh deployment from scratch works
- [ ] Rolling update completes without downtime
- [ ] Pod restart recovers cleanly
- [ ] Scaling to 2 replicas works
- [ ] User can sign up, create tasks, use chat (full flow in K8s)

## Non-Negotiables (Phase IV)

### MUST Have
- Multi-stage Docker builds for all containers
- Specific image version tags (never :latest)
- Non-root user in all containers
- K8s Secrets for all sensitive configuration
- Resource requests AND limits on all containers
- Consistent labels (app, component) on all K8s resources
- Helm charts for all K8s resource management
- Health probes (liveness, readiness) on all deployments
- Stateless containers (no local persistent storage)

### MUST NOT Have
- Hardcoded secrets in ANY file (Dockerfile, Helm values, manifests, scripts)
- :latest image tags
- Root user in containers
- Secrets in ConfigMaps
- Secrets committed to git
- Standalone Pods (must use Deployments)
- Raw kubectl apply in production workflow (use Helm)
- Local file storage in containers
- Host-dependent paths or binaries

## Deployment Standards (Phase IV)

### Local Kubernetes Deployment (Minikube)

#### Prerequisites
```bash
# Required tools
minikube version  # v1.32+
kubectl version   # v1.28+
helm version      # v3.14+
docker version    # v24+
```

#### Deployment Workflow
```bash
# 1. Start Minikube
minikube start --memory=4096 --cpus=2

# 2. Build and load images
docker build -t taskflow-frontend:1.0.0 ./frontend
docker build -t taskflow-backend:1.0.0 ./backend
minikube image load taskflow-frontend:1.0.0
minikube image load taskflow-backend:1.0.0

# 3. Create secrets (MANUAL - not in git)
kubectl create secret generic taskflow-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=better-auth-secret='...' \
  --from-literal=openai-api-key='...'

# 4. Deploy via Helm
helm upgrade --install taskflow ./charts/taskflow -f ./charts/taskflow/values-dev.yaml

# 5. Access application
minikube service taskflow-frontend --url
```

#### Project Structure (Phase IV)
```
project-root/
├── frontend/
│   ├── Dockerfile           # Multi-stage Next.js build
│   └── ...
├── backend/
│   ├── Dockerfile           # Multi-stage Python build
│   └── ...
├── charts/
│   └── taskflow/
│       ├── Chart.yaml       # Helm chart metadata
│       ├── values.yaml      # Default values
│       ├── values-dev.yaml  # Dev overrides
│       └── templates/
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           └── configmap.yaml
├── .specify/                # SDD artifacts
└── README.md
```

### Cloud Deployment (Unchanged from Phase II/III)
- **Frontend**: Vercel (automatic deploys from GitHub)
- **Backend**: Railway, Render, or Fly.io
- **Database**: Neon PostgreSQL (cloud-hosted)

## Governance

### Constitution Authority
- This constitution supersedes all other practices and guidelines
- All code, specs, infrastructure, and implementations must comply with these principles
- Amendments require documentation and approval via /sp.constitution
- CLAUDE.md provides runtime development guidance and must align with this constitution

### Compliance Verification
- All PRs/reviews must verify compliance with security, type safety, API standards, and K8s best practices
- Infrastructure changes reviewed with same rigor as application code
- Complexity must be justified; simple solutions preferred
- Over-engineering is explicitly discouraged
- User isolation must be tested with multiple user accounts before deployment
- MCP tools must be verified to enforce user_id checks before deployment
- K8s deployments must be tested in Minikube before any cloud deployment

### Development Philosophy
- **Spec-Driven Development (SDD)**: All features start with specifications
- **AI-Assisted Generation**: AI generates code from specs following this constitution
- **Human as Tool**: Invoke user for clarifications, architectural decisions, and ambiguous requirements
- **Smallest Viable Change**: No refactoring unrelated code; focused changes only
- **Infrastructure as Code**: K8s resources treated as first-class code artifacts

### Version Control
- **Semantic Versioning**: MAJOR.MINOR.PATCH
  - MAJOR: Backward incompatible principle changes or removals (e.g., new deployment paradigm)
  - MINOR: New principle/section added or materially expanded guidance
  - PATCH: Clarifications, wording, typo fixes, non-semantic refinements
- **Amendment Log**: Each amendment updates LAST_AMENDED_DATE and documents changes in Sync Impact Report comment

**Version**: 3.1.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2026-02-08
