# Feature Specification: TaskFlow Phase IV - Local Kubernetes Deployment

**Feature Branch**: `001-kubernetes`
**Created**: 2026-02-07
**Updated**: 2026-02-08
**Status**: Ready for Planning
**Input**: User description: "Phase IV: TaskFlow Local Kubernetes Deployment - Deploy full-stack app (Next.js frontend + FastAPI backend + Neon DB) to Minikube using Docker containers and Helm charts. Features stay identical to Phase III (Signup/Signin/Task CRUD/Chatbot), but deployment changes from local processes to containerized K8s pods."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Frontend to Minikube (Priority: P1)

A DevOps engineer needs to containerize the Next.js frontend and deploy it to a local Kubernetes cluster for testing cloud-native deployment patterns before moving to production.

**Why this priority**: The frontend is the user-facing component and all other services depend on it being accessible. Without a working frontend deployment, users cannot interact with the application.

**Independent Test**: Can be fully tested by building the frontend Docker image, loading it into Minikube, installing the Helm chart, and verifying that frontend pods are running and accessible via port-forward at http://localhost:3000. The frontend should display the login page without backend connectivity initially.

**Acceptance Scenarios**:

1. **Given** a completed Next.js application in the frontend directory, **When** the DevOps engineer runs `docker build -t taskflow-frontend:latest ./frontend`, **Then** a Docker image is created successfully with size under 200MB and no build errors
2. **Given** a built frontend Docker image, **When** the engineer loads the image to Minikube using `minikube image load taskflow-frontend:latest`, **Then** the image is available in Minikube's local registry
3. **Given** a configured Helm chart with frontend deployment templates, **When** the engineer runs `helm install taskflow helm/ -f helm/values-dev.yaml`, **Then** frontend pods are created and reach Running state within 30 seconds
4. **Given** running frontend pods, **When** the engineer runs `kubectl port-forward svc/taskflow-frontend 3000:3000`, **Then** the application is accessible at http://localhost:3000 and displays the login page

---

### User Story 2 - Deploy Backend to Minikube (Priority: P1)

A DevOps engineer needs to containerize the FastAPI backend and deploy it to Kubernetes so the frontend can communicate with it via Kubernetes service networking.

**Why this priority**: The backend provides all API endpoints for authentication and task management. Without it, the application cannot perform any business logic or data operations.

**Independent Test**: Can be fully tested by building the backend Docker image, loading it into Minikube, deploying via Helm, and verifying that backend pods are running and responding to health check requests at http://localhost:8000/health via port-forward.

**Acceptance Scenarios**:

1. **Given** a completed FastAPI application in the backend directory, **When** the engineer runs `docker build -t taskflow-backend:latest ./backend`, **Then** a Docker image is created successfully with size under 300MB and no build errors
2. **Given** a built backend Docker image, **When** the engineer loads the image to Minikube using `minikube image load taskflow-backend:latest`, **Then** the image is available in Minikube's local registry
3. **Given** a configured Helm chart with backend deployment templates, **When** the engineer runs `helm install taskflow helm/ -f helm/values-dev.yaml`, **Then** backend pods are created and reach Running state within 30 seconds
4. **Given** running backend pods with DATABASE_URL configured, **When** the engineer runs `kubectl port-forward svc/taskflow-backend 8000:8000`, **Then** the API health endpoint responds successfully at http://localhost:8000/health

---

### User Story 3 - Frontend and Backend Communication via K8s Services (Priority: P1)

A DevOps engineer needs to configure Kubernetes Services so that frontend pods can discover and communicate with backend pods using Kubernetes DNS rather than hardcoded IP addresses.

**Why this priority**: Service-to-service communication is core Kubernetes functionality. Without it, the application cannot function as a cohesive system, and users cannot complete any workflows requiring API calls.

**Independent Test**: Can be fully tested by deploying both services, configuring the frontend with the backend service DNS name (taskflow-backend.default.svc.cluster.local), and verifying that API calls from the frontend successfully reach the backend pods. Test by attempting user signup through the frontend UI.

**Acceptance Scenarios**:

1. **Given** frontend and backend deployments are running, **When** Kubernetes Services are created with ClusterIP type, **Then** both services have stable internal IP addresses and are discoverable via DNS
2. **Given** a frontend pod configured with backend service DNS name, **When** the frontend makes an API call to `http://taskflow-backend:8000/api/v1/health`, **Then** the request is routed to a backend pod and returns a 200 status code
3. **Given** both services are running with proper environment variables, **When** a user attempts to sign up via the frontend at http://localhost:3000/signup, **Then** the frontend sends a POST request to the backend service, the backend creates a user record in the Neon database, and the user receives a success confirmation
4. **Given** a user is signed in, **When** they create a new task via the frontend, **Then** the task is persisted in the database via the backend API and appears in the task list immediately

---

### User Story 4 - Access Application via Port Forward (Priority: P1)

A developer needs to access the Kubernetes-deployed application locally for testing and development without setting up ingress controllers or load balancers.

**Why this priority**: Port forwarding is the only practical way to test locally deployed applications in Minikube without additional infrastructure. It's essential for validating that all Phase III features work identically in the Kubernetes environment.

**Independent Test**: Can be fully tested by running `kubectl port-forward` commands for both services and verifying that all Phase III features (signup, signin, task CRUD, chatbot) work identically when accessed via localhost:3000 and localhost:8000.

**Acceptance Scenarios**:

1. **Given** frontend and backend services are running, **When** the developer runs `kubectl port-forward svc/taskflow-frontend 3000:3000` and `kubectl port-forward svc/taskflow-backend 8000:8000` in separate terminals, **Then** both services are accessible at their respective localhost URLs
2. **Given** the application is accessible via port-forward, **When** the developer navigates to http://localhost:3000 and completes the signup flow, **Then** a new user is created successfully and matches the behavior of the Phase III local deployment
3. **Given** a signed-in user via port-forwarded frontend, **When** they perform CRUD operations on tasks (create, read, update, delete), **Then** all operations succeed and data persists across page refreshes
4. **Given** the chatbot feature from Phase III, **When** a user accesses the chatbot via the Kubernetes-deployed frontend, **Then** the chatbot responds identically to the Phase III behavior with no feature regressions

---

### User Story 5 - Scale Deployments and Verify Resilience (Priority: P2)

A DevOps engineer needs to test Kubernetes scaling and self-healing capabilities by increasing replicas and verifying that the application remains available even when pods are deleted.

**Why this priority**: Scaling and resilience are key benefits of Kubernetes. While not required for MVP functionality, demonstrating these capabilities validates the infrastructure design and provides confidence for production deployment.

**Independent Test**: Can be fully tested by updating Helm values to increase replicas from 2 to 3, applying the changes, verifying that new pods are created and load-balanced, and then deleting a pod to confirm automatic replacement.

**Acceptance Scenarios**:

1. **Given** frontend and backend deployments with 2 replicas each, **When** the engineer updates `values-dev.yaml` to set `replicaCount: 3` and runs `helm upgrade taskflow helm/ -f helm/values-dev.yaml`, **Then** Kubernetes creates a third replica for each service and all pods reach Running state
2. **Given** 3 replicas of the frontend are running, **When** multiple users access the application simultaneously via port-forward, **Then** requests are distributed across all three pods (verifiable via pod logs)
3. **Given** 3 replicas of the backend are running, **When** the engineer deletes one backend pod using `kubectl delete pod <pod-name>`, **Then** Kubernetes automatically creates a replacement pod within 10 seconds and the application remains accessible
4. **Given** a running application with multiple replicas, **When** a pod crashes due to an error (simulated by exec into pod and killing the process), **Then** the liveness probe detects the failure, Kubernetes restarts the pod, and users experience no service interruption

---

### Edge Cases

- What happens when a Docker image build fails due to missing dependencies?
  - The build process should output clear error messages indicating which dependency is missing. Developer must fix package.json or requirements.txt before retrying.

- What happens when Helm install fails due to invalid template syntax?
  - Helm returns a validation error with the line number and specific syntax issue. Developer must fix the template YAML and retry installation.

- What happens when frontend cannot reach backend due to misconfigured service DNS?
  - Frontend API calls fail with network errors. Developer must verify that the backend service name matches the DNS configuration in frontend environment variables and that both services are in the same namespace.

- What happens when pods fail readiness probes and never receive traffic?
  - Kubernetes keeps pods in a non-ready state. Developer must check pod logs to identify the readiness probe failure reason (e.g., database connection failure, missing environment variables).

- What happens when the Neon database is unreachable from Kubernetes pods?
  - Backend pods fail to start or fail readiness probes. Developer must verify DATABASE_URL secret is correctly configured and that firewall rules allow connections from the local machine.

- What happens when scaling down from 3 to 1 replica while users are active?
  - Kubernetes terminates 2 pods gracefully. Active sessions may be interrupted if session state is not shared. Users must refresh or re-login.

- What happens when Docker image sizes exceed resource limits?
  - Image pull may be slow or fail if disk space is insufficient. Developer must optimize Dockerfiles using multi-stage builds and remove unnecessary files.

- What happens when ConfigMap or Secret values are updated?
  - Existing pods do not automatically reload new values. Developer must trigger a rolling restart using `kubectl rollout restart deployment/<name>` to apply changes.

## Requirements *(mandatory)*

### Functional Requirements

**Containerization**

- **FR-401**: System MUST provide a Dockerfile for the frontend with multi-stage builds (builder stage using Node.js 20 Alpine for building, runtime stage for serving)
- **FR-402**: Frontend Dockerfile MUST use `npm ci` for deterministic dependency installation and `npm run build` to generate production-optimized static assets
- **FR-403**: Frontend Dockerfile MUST expose port 3000 and use `CMD ["npm", "start"]` to serve the Next.js application
- **FR-404**: System MUST provide a Dockerfile for the backend using Python 3.13-slim as the base image
- **FR-405**: Backend Dockerfile MUST copy requirements.txt, install dependencies via pip, and copy all application code into /app
- **FR-406**: Backend Dockerfile MUST expose port 8000 and use `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]` to start the FastAPI server
- **FR-407**: Dockerfiles MUST NOT contain hardcoded secrets, passwords, API keys, or database credentials
- **FR-408**: Frontend Docker image MUST be under 200MB in size after build optimization
- **FR-409**: Backend Docker image MUST be under 300MB in size after build optimization
- **FR-410**: Docker builds MUST succeed without errors when run with `docker build` command

**Kubernetes Deployments**

- **FR-411**: System MUST provide Kubernetes Deployment manifests for frontend with configurable replica count (default 2)
- **FR-412**: System MUST provide Kubernetes Deployment manifests for backend with configurable replica count (default 2)
- **FR-413**: Frontend Deployment MUST specify the frontend Docker image with tag and imagePullPolicy (Never for Minikube)
- **FR-414**: Backend Deployment MUST specify the backend Docker image with tag and imagePullPolicy (Never for Minikube)
- **FR-415**: Deployments MUST include labels for app name, component (frontend/backend), and version
- **FR-416**: Deployments MUST define container ports matching the application ports (3000 for frontend, 8000 for backend)
- **FR-417**: Deployments MUST inject environment variables from ConfigMaps and Secrets
- **FR-418**: Deployments MUST define resource requests and limits for CPU and memory to prevent resource exhaustion

**Kubernetes Services**

- **FR-419**: System MUST provide a Kubernetes Service for frontend with type ClusterIP and optional NodePort for local access
- **FR-420**: System MUST provide a Kubernetes Service for backend with type ClusterIP and optional NodePort for local access
- **FR-421**: Services MUST select pods using label selectors matching the deployment labels
- **FR-422**: Services MUST expose ports with targetPort matching container ports (3000 for frontend, 8000 for backend)
- **FR-423**: Services MUST be accessible within the cluster via DNS (taskflow-frontend.default.svc.cluster.local, taskflow-backend.default.svc.cluster.local)
- **FR-424**: Services MUST provide stable endpoints for service discovery and load balancing across multiple pod replicas

**Configuration Management**

- **FR-425**: System MUST provide a ConfigMap for non-secret configuration values (FRONTEND_URL, BACKEND_URL, API_ENDPOINT, NODE_ENV)
- **FR-426**: System MUST provide a Secret for sensitive data (DATABASE_URL, BETTER_AUTH_SECRET, API_KEY)
- **FR-427**: ConfigMap values MUST be injected into containers as environment variables via envFrom or env fields
- **FR-428**: Secret values MUST be injected into containers as environment variables via envFrom or env fields with secretKeyRef
- **FR-429**: Configuration MUST support environment-specific overrides (development vs production values)
- **FR-430**: Secrets MUST be base64-encoded in the YAML manifests but never committed to version control with real values

**Health Checks**

- **FR-431**: Backend Deployment MUST include a liveness probe that checks /health endpoint every 10 seconds
- **FR-432**: Backend Deployment MUST include a readiness probe that checks /health endpoint before routing traffic
- **FR-433**: Frontend Deployment MUST include a liveness probe that checks port 3000 availability
- **FR-434**: Frontend Deployment MUST include a readiness probe that ensures the application is ready to serve requests
- **FR-435**: Liveness probes MUST restart unhealthy pods automatically to recover from failures
- **FR-436**: Readiness probes MUST prevent traffic routing to pods that are not ready to handle requests
- **FR-437**: Health probes MUST have appropriate initialDelaySeconds (30s) to allow application startup time
- **FR-438**: Health probes MUST have failureThreshold (3) to avoid false positives from transient issues

**Helm Chart**

- **FR-439**: System MUST provide a Helm chart with Chart.yaml containing metadata (name: taskflow, apiVersion: v2, version, description)
- **FR-440**: Helm chart MUST include values.yaml with default configuration values (replicaCount: 2, image names and tags, service ports)
- **FR-441**: Helm chart MUST include values-dev.yaml with development-specific overrides (replicaCount: 1, imagePullPolicy: Never)
- **FR-442**: Helm chart templates directory MUST contain frontend-deployment.yaml and backend-deployment.yaml
- **FR-443**: Helm chart templates directory MUST contain frontend-service.yaml and backend-service.yaml
- **FR-444**: Helm chart templates directory MUST contain configmap.yaml and secrets.yaml templates
- **FR-445**: Helm chart MUST support optional ingress.yaml template for routing / to frontend and /api to backend
- **FR-446**: Helm chart MUST include NOTES.txt with post-installation instructions for port-forwarding and verification
- **FR-447**: Helm chart MUST use Go templating to inject values from values.yaml into Kubernetes manifests
- **FR-448**: Helm chart MUST pass `helm lint` validation with zero errors

**Installation and Deployment**

- **FR-449**: System MUST support installation via `helm install taskflow helm/ -f helm/values-dev.yaml` command
- **FR-450**: Installation MUST create all required Kubernetes resources (Deployments, Services, ConfigMaps, Secrets) in a single operation
- **FR-451**: Frontend pods MUST reach Running state within 30 seconds of Helm installation
- **FR-452**: Backend pods MUST reach Running state within 30 seconds of Helm installation
- **FR-453**: System MUST support uninstallation via `helm uninstall taskflow` which removes all created resources
- **FR-454**: System MUST support upgrading configuration via `helm upgrade taskflow helm/ -f helm/values-dev.yaml`

**Scaling and Resilience**

- **FR-455**: System MUST support horizontal scaling by updating replicaCount in values.yaml and running `helm upgrade`
- **FR-456**: Kubernetes MUST automatically load-balance traffic across all available pod replicas
- **FR-457**: When a pod is deleted manually, Kubernetes MUST automatically create a replacement pod to maintain desired replica count
- **FR-458**: When a pod crashes, Kubernetes MUST automatically restart the pod using liveness probe detection
- **FR-459**: System MUST maintain application availability during rolling updates with zero downtime
- **FR-460**: System MUST support scaling from 1 to 3 replicas for both frontend and backend without manual configuration changes

**Data Persistence**

- **FR-461**: Application data MUST persist in the external Neon PostgreSQL database
- **FR-462**: Containers MUST be stateless with no local data storage requirements
- **FR-463**: When pods restart, application state MUST be preserved via the external database
- **FR-464**: Database connection string (DATABASE_URL) MUST be configured via Kubernetes Secret

**Local Access**

- **FR-465**: Developers MUST be able to access the frontend via `kubectl port-forward svc/taskflow-frontend 3000:3000`
- **FR-466**: Developers MUST be able to access the backend via `kubectl port-forward svc/taskflow-backend 8000:8000`
- **FR-467**: Port-forwarded services MUST behave identically to Phase III local deployment
- **FR-468**: All Phase III features (signup, signin, task CRUD, chatbot) MUST work without modification in Kubernetes environment

**Feature Parity**

- **FR-469**: User signup functionality MUST work identically in Kubernetes as in Phase III local deployment
- **FR-470**: User signin functionality MUST work identically in Kubernetes as in Phase III local deployment
- **FR-471**: Task creation, reading, updating, and deletion MUST work identically in Kubernetes as in Phase III local deployment
- **FR-472**: AI chatbot functionality from Phase III MUST work identically in Kubernetes environment
- **FR-473**: Better Auth JWT authentication MUST work identically across containerized services
- **FR-474**: All existing API endpoints MUST respond correctly when deployed in Kubernetes

**Command Automation (Claude Code Executed)**

- **FR-475**: Claude Code MUST execute `docker build -t taskflow-frontend:1.0.0 ./frontend` to build the frontend image
- **FR-476**: Claude Code MUST execute `docker build -t taskflow-backend:1.0.0 ./backend` to build the backend image
- **FR-477**: Claude Code MUST execute `minikube image load taskflow-frontend:1.0.0` to load the frontend image into Minikube
- **FR-478**: Claude Code MUST execute `minikube image load taskflow-backend:1.0.0` to load the backend image into Minikube
- **FR-479**: Claude Code MUST execute `kubectl create secret generic taskflow-secrets --from-literal=...` with user-provided secret values
- **FR-480**: Claude Code MUST execute `helm lint helm/` to validate the Helm chart before installation
- **FR-481**: Claude Code MUST execute `helm upgrade --install taskflow helm/ -f helm/values-dev.yaml` to deploy the application
- **FR-482**: Claude Code MUST execute `kubectl get pods` and verify all pods reach Running state
- **FR-483**: Claude Code MUST execute `kubectl get services` and verify services are created with correct ports
- **FR-484**: Claude Code MUST execute `kubectl port-forward svc/taskflow-frontend 3000:3000` for user browser testing
- **FR-485**: Claude Code MUST execute `kubectl port-forward svc/taskflow-backend 8000:8000` for API access
- **FR-486**: Claude Code MUST execute `kubectl logs` to diagnose pod startup issues when pods fail
- **FR-487**: Claude Code MUST execute `kubectl describe pod` to troubleshoot scheduling or configuration issues
- **FR-488**: Claude Code MUST execute `helm upgrade taskflow helm/ -f helm/values-dev.yaml` to apply configuration changes
- **FR-489**: Claude Code MUST execute `kubectl scale deployment` or Helm upgrade to scale replicas
- **FR-490**: User MUST NOT be required to manually type or copy-paste any infrastructure commands

### Key Entities

**Docker Images**

- **taskflow-frontend**: Container image for the Next.js frontend application, built from frontend/Dockerfile, includes all static assets and Node.js runtime for serving
- **taskflow-backend**: Container image for the FastAPI backend application, built from backend/Dockerfile, includes Python runtime and all API code

**Kubernetes Resources**

- **Deployment (taskflow-frontend)**: Kubernetes Deployment managing frontend pod replicas, includes container spec, environment variables, health probes
- **Deployment (taskflow-backend)**: Kubernetes Deployment managing backend pod replicas, includes container spec, environment variables, health probes
- **Service (taskflow-frontend)**: Kubernetes Service providing stable endpoint and load balancing for frontend pods
- **Service (taskflow-backend)**: Kubernetes Service providing stable endpoint and load balancing for backend pods
- **ConfigMap**: Non-secret configuration data injected into containers as environment variables
- **Secret**: Sensitive data (database URL, auth secrets) injected into containers securely

**Helm Resources**

- **Chart.yaml**: Helm chart metadata including name, version, and description
- **values.yaml**: Default configuration values used across all environments
- **values-dev.yaml**: Development-specific overrides for local Minikube deployment

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-401**: Frontend Docker image builds successfully in under 3 minutes with final size under 200MB
- **SC-402**: Backend Docker image builds successfully in under 2 minutes with final size under 300MB
- **SC-403**: Helm chart validation passes with zero errors when running `helm lint helm/`
- **SC-404**: Helm installation completes successfully in under 60 seconds
- **SC-405**: Frontend pods reach Running state within 30 seconds of deployment
- **SC-406**: Backend pods reach Running state within 30 seconds of deployment
- **SC-407**: Frontend service is accessible via port-forward at http://localhost:3000 within 5 seconds
- **SC-408**: Backend service is accessible via port-forward at http://localhost:8000 within 5 seconds
- **SC-409**: Frontend can successfully communicate with backend via Kubernetes Service DNS without hardcoded IP addresses
- **SC-410**: User signup workflow completes successfully in under 3 seconds via Kubernetes-deployed application
- **SC-411**: User signin workflow completes successfully in under 2 seconds via Kubernetes-deployed application
- **SC-412**: Task creation via Kubernetes-deployed application completes in under 1 second
- **SC-413**: Task list retrieval via Kubernetes-deployed application completes in under 500ms
- **SC-414**: Task update operations via Kubernetes-deployed application complete in under 1 second
- **SC-415**: Task deletion operations via Kubernetes-deployed application complete in under 1 second
- **SC-416**: AI chatbot responds within 3 seconds when deployed in Kubernetes environment
- **SC-417**: Database connection from backend pods to Neon PostgreSQL succeeds on first startup attempt
- **SC-418**: Scaling from 2 to 3 replicas completes within 30 seconds with all new pods reaching Running state
- **SC-419**: Deleting a pod results in automatic replacement within 10 seconds
- **SC-420**: Application remains available with zero downtime when one replica is manually terminated
- **SC-421**: Data persists correctly across pod restarts with no data loss
- **SC-422**: Health probes detect unhealthy pods within 30 seconds and trigger automatic restarts
- **SC-423**: All Phase III features show zero regression in functionality when deployed to Kubernetes
- **SC-424**: Application handles 50 concurrent users across multiple pod replicas without degradation
- **SC-425**: Configuration changes via ConfigMap updates are applied successfully after pod restart
- **SC-426**: Secret rotation is possible without application downtime via rolling restart
- **SC-427**: Minikube cluster resources (CPU, memory) remain under 4GB total usage for both services
- **SC-428**: Application startup time from Helm install to fully functional state is under 2 minutes
- **SC-429**: Developer can successfully run `helm install`, verify deployment, and access all features following README instructions without errors
- **SC-430**: Application uninstallation via `helm uninstall` removes all resources completely with no orphaned pods or services

## Non-Functional Requirements *(mandatory)*

### Command Automation (Critical)

- All Docker build, Helm install, kubectl, and minikube commands MUST be executed by Claude Code automatically
- User MUST NOT be required to copy-paste or manually type any infrastructure commands
- Claude Code MUST handle command failures, diagnose issues, and retry or escalate appropriately
- Claude Code MUST provide clear progress feedback during long-running operations (building, deploying, verifying)
- Commands MUST be designed to be idempotent and safe to re-run without side effects
- User involvement is limited to: providing secret values verbally, browser testing via localhost, and approval gates for destructive operations

### Deployment Reliability

- Kubernetes self-healing mechanisms ensure that crashed pods are automatically restarted without manual intervention
- Users experience no service interruption when individual pods fail due to replica redundancy
- Health probes (liveness and readiness) accurately detect application health and prevent traffic to unhealthy instances
- Rolling updates maintain application availability with zero downtime during configuration changes

### Scalability

- Application supports horizontal scaling from 1 to 3 replicas for both frontend and backend without code changes
- Service load balancing distributes traffic evenly across all available pod replicas
- Resource requests and limits prevent resource contention and ensure predictable performance under load
- Scaling operations complete quickly (under 30 seconds) with minimal operational overhead

### Portability

- Helm charts are environment-agnostic and work in both Minikube and cloud Kubernetes providers (GKE, EKS, AKS)
- Environment-specific configuration is managed via separate values files (values-dev.yaml, values-prod.yaml)
- Docker images are built with multi-stage builds for optimal size and portability across platforms
- No hardcoded dependencies on local file paths or Minikube-specific features

### Validation and Quality

- Helm chart passes `helm lint` validation with zero errors
- Docker images build successfully on multiple platforms (Linux, macOS, Windows with WSL2)
- Kubernetes manifests follow best practices for labels, selectors, and resource management
- Configuration separation ensures no secrets are committed to version control

### Documentation Clarity

- README includes step-by-step instructions for Docker image building, Minikube setup, and Helm installation
- NOTES.txt in Helm chart provides immediate next steps after installation (port-forward commands, verification steps)
- Error messages clearly indicate failure points with actionable resolution steps
- First-time users can successfully deploy the application following documentation without external support

### Image Optimization

- Multi-stage Docker builds minimize final image sizes by excluding build tools and intermediate artifacts
- Frontend image uses Alpine Linux base for minimal footprint
- Backend image uses slim Python variant to reduce size while maintaining required dependencies
- Image layers are optimized to maximize Docker cache efficiency during iterative development

### Configuration Management

- All configuration values are externalized to ConfigMaps and Secrets
- No environment-specific values are hardcoded in application code or Dockerfiles
- Sensitive data (database URLs, API keys) are managed via Kubernetes Secrets with base64 encoding
- Configuration changes can be applied via `helm upgrade` without rebuilding Docker images

### Security

- Docker images run as non-root users where possible to minimize security risks
- Secrets are never logged or exposed in container stdout/stderr
- Health check endpoints do not expose sensitive application internals
- Database credentials are injected via environment variables and never hardcoded

## Assumptions *(mandatory)*

- **Minikube Environment**: Deployment targets a local Minikube Kubernetes cluster on a developer laptop with at least 8GB RAM and 4 CPU cores available
- **Docker Desktop**: Docker is installed and running locally for building container images
- **Helm 3**: Helm 3.x is installed and available on the system PATH
- **External Database**: Neon PostgreSQL database is already provisioned and accessible from the local machine (DATABASE_URL is known)
- **Better Auth Secret**: BETTER_AUTH_SECRET from Phase III is available for configuring authentication in Kubernetes
- **No Ingress Controller**: Local testing uses port-forward instead of ingress controllers for simplicity
- **Single Namespace**: All resources are deployed to the default Kubernetes namespace
- **ImagePullPolicy Never**: Minikube uses locally loaded Docker images with imagePullPolicy: Never (no external registry required)
- **No Persistent Volumes**: Application is stateless and stores all data in the external Neon database (no PVCs needed)
- **HTTP Only**: Local deployment uses HTTP (not HTTPS) for simplicity; production would add TLS termination
- **Development Mode**: Phase IV focuses on development deployment patterns; production hardening (RBAC, NetworkPolicies, PodSecurityPolicies) is future work

## Out of Scope *(mandatory)*

- **Production Kubernetes Deployment**: Deploying to cloud providers (GKE, EKS, AKS) is out of scope; this phase focuses on local Minikube
- **Ingress Controllers**: Setting up ingress controllers and ingress resources is optional and not required for core functionality
- **TLS/SSL Certificates**: HTTPS configuration is not required for local testing
- **CI/CD Pipelines**: Automated build and deployment pipelines are not included in Phase IV
- **Monitoring and Logging**: Prometheus, Grafana, ELK stack, or other observability tools are not configured
- **Service Mesh**: Istio, Linkerd, or other service mesh implementations are not included
- **Persistent Volumes**: StatefulSets and persistent volume claims for stateful workloads are not needed
- **Database Migration Jobs**: Kubernetes Jobs for running database migrations are not included (manual migration assumed)
- **RBAC and Security Policies**: Role-based access control, pod security policies, and network policies are deferred to production deployment
- **Horizontal Pod Autoscaling**: Automated scaling based on CPU/memory metrics is not configured (manual scaling only)
- **Multi-Environment Helm Releases**: Managing staging and production releases via Helm is out of scope
- **Container Registry**: Pushing images to Docker Hub or private registries is not required (Minikube loads local images)

## Dependencies *(mandatory)*

- **Phase III Completion**: All Phase III features (signup, signin, task CRUD, AI chatbot) must be fully functional locally before containerization
- **Docker Installation**: Docker Desktop or Docker Engine must be installed and running
- **Minikube Installation**: Minikube must be installed and a cluster must be running (`minikube start`)
- **kubectl Installation**: kubectl CLI must be installed and configured to communicate with Minikube
- **Helm Installation**: Helm 3.x must be installed on the local machine
- **Neon Database**: A provisioned Neon PostgreSQL database with valid DATABASE_URL connection string
- **Better Auth Secret**: The BETTER_AUTH_SECRET value used in Phase III must be available for Kubernetes Secrets
- **Node.js 20**: Required for building the frontend Docker image
- **Python 3.13**: Required for building the backend Docker image
- **Git**: Required for version control and checking out the feature branch

## Risks *(optional)*

- **Docker Image Size**: Without proper optimization, images may exceed size targets (200MB frontend, 300MB backend), causing slow image loading to Minikube
  - *Mitigation*: Use multi-stage builds, Alpine base images, and .dockerignore files to exclude unnecessary files

- **Resource Constraints**: Minikube may run out of CPU or memory when running multiple pod replicas on a developer laptop
  - *Mitigation*: Use values-dev.yaml to reduce replicas to 1 in development, document minimum system requirements

- **Service Discovery Issues**: Frontend may fail to reach backend if Kubernetes DNS is misconfigured or service names don't match
  - *Mitigation*: Test service-to-service communication early, use clear naming conventions, document expected DNS names

- **Database Connectivity**: Backend pods may fail to connect to Neon database due to firewall rules or incorrect DATABASE_URL
  - *Mitigation*: Test database connectivity locally before containerizing, ensure DATABASE_URL includes proper SSL parameters

- **Secret Management**: Developers may accidentally commit Kubernetes Secrets with real credentials to version control
  - *Mitigation*: Use .gitignore for secrets.yaml, provide template files with placeholder values, document secret creation process

- **Health Probe Failures**: Pods may never reach Ready state if health probes are misconfigured or application startup is slow
  - *Mitigation*: Use appropriate initialDelaySeconds (30s) and failureThreshold (3) values, test probes locally

- **Helm Chart Complexity**: Incorrect Go templating or YAML syntax may cause Helm install to fail
  - *Mitigation*: Run `helm lint` frequently during development, test with different values files

## Open Questions

- Should we include an optional ingress configuration for developers who want to test ingress patterns locally?
  - *Assumption*: Include ingress.yaml as an optional template but document port-forward as the primary local access method

- What CPU and memory resource limits should we set for each container?
  - *Assumption*: Frontend requests 100m CPU / 128Mi memory, limits 500m CPU / 512Mi memory; Backend requests 200m CPU / 256Mi memory, limits 1000m CPU / 1Gi memory

- Should we configure horizontal pod autoscaling (HPA) even though it's not required for Phase IV?
  - *Assumption*: HPA is out of scope; manual scaling via `helm upgrade` is sufficient for Phase IV

- Should we create separate Kubernetes namespaces for different environments (dev, staging)?
  - *Assumption*: Use default namespace for simplicity; namespace management is deferred to production deployment

- Should we include Kubernetes Jobs for running database migrations?
  - *Assumption*: Database migrations are run manually before deployment; automated migration jobs are out of scope for Phase IV
