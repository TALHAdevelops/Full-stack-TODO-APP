# Docker Contracts - Phase IV

**Date**: 2026-02-07
**Purpose**: Define the contracts for Docker images, Dockerfiles, and image naming conventions

## Frontend Dockerfile Contract

### Base Image
- **Required**: `node:20-alpine`
- **Rationale**: Alpine variant is 40MB vs 180MB for debian; sufficient for Next.js runtime

### Multi-Stage Build Structure
```dockerfile
# Stage 1: Builder
FROM node:20-alpine AS builder
# Install dependencies, build Next.js app
# Output: .next/standalone/

# Stage 2: Runner
FROM node:20-alpine AS runner
# Copy only runtime artifacts from builder
# Run as non-root user
```

### Exposed Port
- **Port**: 3000
- **Protocol**: HTTP

### Entry Command
```dockerfile
CMD ["node", "server.js"]
```
- **Working Directory**: /app
- **User**: nextjs (UID 1001, non-root)

### Environment Variables (injected at runtime)
- `BACKEND_URL`: Backend service URL (from ConfigMap)
- `NODE_ENV`: production|development (from ConfigMap)

### Size Target
- **Maximum**: 200MB
- **Typical**: 150-180MB (Next.js standalone + Node.js runtime)

### .dockerignore Requirements
Must exclude:
```
node_modules
.next
.git
.env*
README.md
*.md
.vscode
.idea
```

---

## Backend Dockerfile Contract

### Base Image
- **Required**: `python:3.13-slim`
- **Rationale**: slim variant is 120MB vs 180MB full; includes glibc for native extensions (psycopg2, cryptography)

### Multi-Stage Build Structure
```dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder
# Install build dependencies (gcc, etc.)
# Compile Python wheels
# Output: /root/.local/

# Stage 2: Runner
FROM python:3.13-slim AS runner
# Copy only site-packages from builder
# No build tools in final image
```

### Exposed Port
- **Port**: 8000
- **Protocol**: HTTP

### Entry Command
```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
- **Working Directory**: /app
- **User**: appuser (UID 1000, non-root recommended but optional for Python)

### Environment Variables (injected at runtime)
- `DATABASE_URL`: Neon PostgreSQL connection string (from Secret)
- `BETTER_AUTH_SECRET`: JWT signing secret (from Secret)
- `OPENAI_API_KEY`: OpenAI API key for chatbot (from Secret)
- `FRONTEND_URL`: Frontend service URL (from ConfigMap, for CORS)

### Size Target
- **Maximum**: 300MB
- **Typical**: 250-280MB (Python 3.13 + FastAPI + SQLModel + OpenAI SDK)

### .dockerignore Requirements
Must exclude:
```
__pycache__
*.pyc
*.pyo
.venv
venv
.git
.env*
tests/
*.md
.pytest_cache
```

---

## Image Naming Convention

### Format
```
<repository>:<tag>
```

### Repository Naming
- **Frontend**: `taskflow-frontend`
- **Backend**: `taskflow-backend`
- **Pattern**: `<project>-<component>`

### Tag Naming
- **Semantic Versioning**: `MAJOR.MINOR.PATCH` (e.g., `1.0.0`, `1.2.3`)
- **Development**: `latest` (only for local dev, NEVER in production)
- **Feature Branches**: `<version>-<branch>` (e.g., `1.0.0-kubernetes`)

### Full Examples
- `taskflow-frontend:1.0.0` (production-ready)
- `taskflow-backend:1.0.0` (production-ready)
- `taskflow-frontend:latest` (local development only)

### Image Pull Policy
- **Minikube (local)**: `imagePullPolicy: Never` (uses locally loaded images)
- **Production (cloud)**: `imagePullPolicy: IfNotPresent` (pulls from registry if not cached)

---

## Build Contracts

### Build Command
```bash
# Frontend
docker build -t taskflow-frontend:1.0.0 ./frontend

# Backend
docker build -t taskflow-backend:1.0.0 ./backend
```

### Build Context
- **Frontend**: `./frontend/` (root of frontend directory)
- **Backend**: `./backend/` (root of backend directory)
- **Never**: Repository root (avoids uploading unnecessary files to Docker daemon)

### Build Arguments
- **MUST NOT** include secrets or passwords
- **MAY** include build-time configuration (e.g., `--build-arg NODE_ENV=production`)

### Layer Caching Strategy
```dockerfile
# Good: Install dependencies before copying code
COPY package*.json ./
RUN npm ci
COPY . .

# Bad: Copy all files first (invalidates cache on any code change)
COPY . .
RUN npm ci
```

---

## Runtime Contracts

### Health Check Endpoint (Backend Only)
- **Path**: `/health`
- **Method**: GET
- **Success Response**: `200 OK` with `{"status": "healthy"}`
- **Failure Response**: `503 Service Unavailable` (if database unreachable)

### Startup Time
- **Frontend**: <15 seconds (Next.js server startup)
- **Backend**: <20 seconds (FastAPI app startup + database connection test)

### Graceful Shutdown
- **Signal**: SIGTERM (sent by Kubernetes)
- **Behavior**:
  - Frontend: Finish processing active requests, then exit
  - Backend: Close database connections, finish active requests, then exit
- **Timeout**: 30 seconds (terminationGracePeriodSeconds in K8s)

### Resource Usage Expectations
- **Frontend**:
  - CPU: <100m at idle, spikes to 250m during SSR
  - Memory: <128Mi at idle, up to 256Mi under load
- **Backend**:
  - CPU: <250m at idle, spikes to 500m during heavy API traffic
  - Memory: <256Mi at idle, up to 512Mi with many concurrent connections

---

## Security Contracts

### Non-Root User
- **Requirement**: All containers MUST run as non-root user
- **Frontend**: `adduser -S nextjs -u 1001` and `USER nextjs`
- **Backend**: `adduser -S appuser -u 1000` and `USER appuser` (optional but recommended)

### No Secrets in Image Layers
- **Requirement**: NEVER use `ENV` or `ARG` for secrets in Dockerfile
- **Enforcement**: Secrets injected via Kubernetes Secrets at runtime

### Minimal Base Images
- **Requirement**: Use alpine or slim variants only
- **Rationale**: Fewer packages = smaller attack surface

### Read-Only Filesystem (Future)
- **Goal**: Set `readOnlyRootFilesystem: true` in K8s Pod spec
- **Blocker**: Next.js standalone mode may require writable /tmp
- **Deferred**: Not required for Phase IV

---

## Validation Checklist

**Pre-Deployment**:
- [ ] Docker build completes without errors
- [ ] Image size within target (<200MB frontend, <300MB backend)
- [ ] Image runs successfully with `docker run -p 3000:3000 taskflow-frontend:1.0.0`
- [ ] Health check endpoint responds correctly (backend only)
- [ ] No secrets in image layers (verify with `docker history`)
- [ ] .dockerignore excludes unnecessary files
- [ ] Container runs as non-root user (verify with `docker exec <container> whoami`)

**Post-Deployment**:
- [ ] Image loads successfully into Minikube (`minikube image load`)
- [ ] Pods start within 30 seconds
- [ ] Health probes pass consistently
- [ ] Application functionality identical to local deployment

---

## Change Management

**When to Update Docker Contracts**:
- New environment variable required
- Port change
- Base image version upgrade
- Entry command change
- Security hardening requirement

**Amendment Process**:
1. Update this contract document
2. Update Dockerfile(s) to match
3. Rebuild images
4. Test in Minikube
5. Document in plan.md

**Backward Compatibility**:
- Breaking changes (port, entry command) require new major version (2.0.0)
- Additive changes (new env var) require new minor version (1.1.0)
- Patch changes (bug fix) increment patch version (1.0.1)
