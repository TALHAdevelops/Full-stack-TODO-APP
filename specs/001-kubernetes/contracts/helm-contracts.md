# Helm Chart Contracts - Phase IV

**Date**: 2026-02-07
**Purpose**: Define contracts for Helm chart structure, values, and templating patterns

## Chart Metadata Contract (Chart.yaml)

### Required Fields
```yaml
apiVersion: v2                  # Helm 3 chart
name: taskflow                  # Chart name (lowercase, no spaces)
version: 1.0.0                  # Chart version (semantic versioning)
appVersion: "1.0.0"             # Application version (semantic versioning)
description: TaskFlow multi-user todo application with AI chatbot and Kubernetes deployment
type: application               # Not a library chart
```

### Optional Fields (Recommended)
```yaml
keywords:
  - todo
  - fastapi
  - nextjs
  - kubernetes
  - helm
maintainers:
  - name: TaskFlow Team
    email: team@taskflow.dev
home: https://github.com/yourusername/taskflow
sources:
  - https://github.com/yourusername/taskflow
```

---

## Values Contract (values.yaml)

### Structure Requirements

**Top-Level Sections**:
1. `replicaCount` - Default replica count for both services
2. `frontend` - Frontend-specific configuration
3. `backend` - Backend-specific configuration
4. `config` - Non-sensitive configuration (ConfigMap)
5. `secrets` - Secret references (NOT secret values)
6. `ingress` - Ingress configuration (optional)

### Default Values Schema
```yaml
# Global replica count (can be overridden per service)
replicaCount: 2

# Frontend configuration
frontend:
  image:
    repository: taskflow-frontend
    tag: "1.0.0"                # MUST be specific version
    pullPolicy: IfNotPresent    # Never for Minikube, IfNotPresent for cloud

  service:
    type: NodePort              # NodePort for Minikube, ClusterIP for cloud with Ingress
    port: 80                    # External service port
    targetPort: 3000            # Container port

  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "250m"

  probes:
    liveness:
      enabled: true
      initialDelaySeconds: 30
      periodSeconds: 10
      failureThreshold: 3
    readiness:
      enabled: true
      initialDelaySeconds: 10
      periodSeconds: 5
      failureThreshold: 3

# Backend configuration
backend:
  image:
    repository: taskflow-backend
    tag: "1.0.0"
    pullPolicy: IfNotPresent

  service:
    type: ClusterIP             # Always ClusterIP (internal only)
    port: 8000
    targetPort: 8000

  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

  probes:
    liveness:
      enabled: true
      initialDelaySeconds: 30
      periodSeconds: 10
      failureThreshold: 3
    readiness:
      enabled: true
      initialDelaySeconds: 10
      periodSeconds: 5
      failureThreshold: 3

# Non-sensitive configuration (injected via ConfigMap)
config:
  frontendUrl: "http://taskflow-frontend"
  backendUrl: "http://taskflow-backend:8000"
  nodeEnv: "production"
  logLevel: "info"

# Secret references (NOT secret values!)
secrets:
  secretName: "taskflow-secrets"  # Name of K8s Secret (created manually)
  keys:
    databaseUrl: "database-url"
    betterAuthSecret: "better-auth-secret"
    openaiApiKey: "openai-api-key"

# Ingress (optional, disabled by default)
ingress:
  enabled: false
  className: "nginx"
  annotations: {}
  hosts:
    - host: taskflow.local
      paths:
        - path: /
          pathType: Prefix
          backend: frontend
        - path: /api
          pathType: Prefix
          backend: backend
  tls: []
```

### Environment-Specific Overrides (values-dev.yaml)
```yaml
# Development overrides for local Minikube
replicaCount: 1  # Single replica for dev

frontend:
  image:
    pullPolicy: Never  # Use locally loaded image

backend:
  image:
    pullPolicy: Never

config:
  nodeEnv: "development"
  logLevel: "debug"
```

---

## Template Contract

### Template Directory Structure
```
templates/
├── _helpers.tpl              # Go template helpers (labels, selectors)
├── frontend-deployment.yaml  # Frontend Deployment manifest
├── frontend-service.yaml     # Frontend Service manifest
├── backend-deployment.yaml   # Backend Deployment manifest
├── backend-service.yaml      # Backend Service manifest
├── configmap.yaml            # ConfigMap for non-sensitive config
├── secrets.yaml              # Secret template (placeholder only)
├── ingress.yaml              # Optional ingress (conditional on .Values.ingress.enabled)
└── NOTES.txt                 # Post-install instructions
```

### Templating Patterns

**Standard Labels (from _helpers.tpl)**:
```yaml
{{- define "taskflow.labels" -}}
app: {{ .Chart.Name }}
version: {{ .Chart.AppVersion }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{- define "taskflow.frontend.labels" -}}
{{ include "taskflow.labels" . }}
component: frontend
{{- end }}

{{- define "taskflow.backend.labels" -}}
{{ include "taskflow.labels" . }}
component: backend
{{- end }}
```

**Values Substitution**:
```yaml
# Deployment replica count
replicas: {{ .Values.replicaCount }}

# Image reference
image: {{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}
imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}

# Resource limits
resources:
  requests:
    memory: {{ .Values.frontend.resources.requests.memory }}
    cpu: {{ .Values.frontend.resources.requests.cpu }}
  limits:
    memory: {{ .Values.frontend.resources.limits.memory }}
    cpu: {{ .Values.frontend.resources.limits.cpu }}
```

**Conditional Resources**:
```yaml
# ingress.yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ .Chart.Name }}-ingress
spec:
  # ... ingress spec
{{- end }}
```

---

## Secret Management Contract

### CRITICAL RULES
1. **NEVER** store real secret values in values.yaml or git
2. **ONLY** store secret references (Secret name and key names)
3. Secrets created manually: `kubectl create secret generic taskflow-secrets --from-literal=...`

### secrets.yaml Template (Placeholder Only)
```yaml
# This file is a TEMPLATE for documentation purposes.
# DO NOT create real secrets via Helm (NEVER committed to git).
# Create secrets manually: kubectl create secret generic taskflow-secrets \
#   --from-literal=database-url='...' \
#   --from-literal=better-auth-secret='...' \
#   --from-literal=openai-api-key='...'

apiVersion: v1
kind: Secret
metadata:
  name: {{ .Values.secrets.secretName }}
type: Opaque
data:
  # Values are base64-encoded but should be created manually
  # database-url: <base64-encoded-value>
  # better-auth-secret: <base64-encoded-value>
  # openai-api-key: <base64-encoded-value>
```

### Secret Injection in Deployments
```yaml
# backend-deployment.yaml
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secrets.secretName }}
      key: {{ .Values.secrets.keys.databaseUrl }}
- name: BETTER_AUTH_SECRET
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secrets.secretName }}
      key: {{ .Values.secrets.keys.betterAuthSecret }}
- name: OPENAI_API_KEY
  valueFrom:
    secretKeyRef:
      name: {{ .Values.secrets.secretName }}
      key: {{ .Values.secrets.keys.openaiApiKey }}
```

---

## ConfigMap Contract

### configmap.yaml Structure
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Chart.Name }}-config
  labels:
    {{- include "taskflow.labels" . | nindent 4 }}
data:
  FRONTEND_URL: {{ .Values.config.frontendUrl | quote }}
  BACKEND_URL: {{ .Values.config.backendUrl | quote }}
  NODE_ENV: {{ .Values.config.nodeEnv | quote }}
  LOG_LEVEL: {{ .Values.config.logLevel | quote }}
```

### ConfigMap Injection in Deployments
```yaml
# frontend-deployment.yaml
envFrom:
- configMapRef:
    name: {{ .Chart.Name }}-config
```

---

## NOTES.txt Contract

### Post-Install Instructions Format
```text
TaskFlow has been deployed to your Kubernetes cluster!

DEPLOYMENT STATUS:
  Release Name:   {{ .Release.Name }}
  Namespace:      {{ .Release.Namespace }}
  Chart Version:  {{ .Chart.Version }}
  App Version:    {{ .Chart.AppVersion }}

ACCESSING THE APPLICATION:

{{- if .Values.ingress.enabled }}
  Ingress is enabled. Access the application at:
  {{- range .Values.ingress.hosts }}
    http://{{ .host }}
  {{- end }}
{{- else }}
  Use port-forward to access the services:

  Frontend:
    kubectl port-forward -n {{ .Release.Namespace }} svc/{{ .Chart.Name }}-frontend 3000:80
    Then visit: http://localhost:3000

  Backend:
    kubectl port-forward -n {{ .Release.Namespace }} svc/{{ .Chart.Name }}-backend 8000:8000
    Then visit: http://localhost:8000/docs
{{- end }}

VERIFY DEPLOYMENT:
  kubectl get pods -n {{ .Release.Namespace }} -l app={{ .Chart.Name }}
  kubectl get services -n {{ .Release.Namespace }} -l app={{ .Chart.Name }}

TROUBLESHOOTING:
  View logs:
    kubectl logs -n {{ .Release.Namespace }} -l app={{ .Chart.Name }},component=frontend
    kubectl logs -n {{ .Release.Namespace }} -l app={{ .Chart.Name }},component=backend

  Check pod status:
    kubectl describe pod -n {{ .Release.Namespace }} <pod-name>

NEXT STEPS:
  1. Create a user account at http://localhost:3000/signup
  2. Sign in and create your first task
  3. Try the AI chatbot!

For more information, visit: https://github.com/yourusername/taskflow
```

---

## Helm Command Contracts

### Install
```bash
helm install taskflow ./helm/ -f ./helm/values-dev.yaml
```
- **Chart Path**: `./helm/` (relative to repository root)
- **Release Name**: `taskflow` (can be customized)
- **Values File**: `-f ./helm/values-dev.yaml` (always specify environment-specific values)

### Upgrade
```bash
helm upgrade taskflow ./helm/ -f ./helm/values-dev.yaml
```
- **Behavior**: Updates existing release with new values
- **Rollout**: Triggers rolling update of Deployments
- **Rollback**: Use `helm rollback taskflow <revision>` if needed

### Uninstall
```bash
helm uninstall taskflow
```
- **Behavior**: Deletes all resources created by the chart
- **Note**: Does NOT delete manually created Secrets

### Lint
```bash
helm lint ./helm/
```
- **Requirement**: MUST pass with zero errors before deployment
- **Validates**: YAML syntax, template rendering, required fields

### Template (Dry Run)
```bash
helm template taskflow ./helm/ -f ./helm/values-dev.yaml
```
- **Output**: Rendered YAML manifests without deploying
- **Use Case**: Verify templating logic before actual deployment

---

## Versioning Contract

### Chart Version (Chart.yaml)
- **Format**: Semantic versioning (MAJOR.MINOR.PATCH)
- **MAJOR**: Breaking changes to chart structure or values schema
- **MINOR**: New optional features (e.g., ingress support)
- **PATCH**: Bug fixes, documentation updates

### App Version (Chart.yaml)
- **Format**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Meaning**: Version of the TaskFlow application (not the chart itself)
- **Sync**: Should match Docker image tags (e.g., `appVersion: "1.0.0"` → `taskflow-frontend:1.0.0`)

### Image Tags (values.yaml)
- **Requirement**: MUST be specific versions, NEVER `:latest`
- **Example**: `tag: "1.0.0"` ✅, `tag: "latest"` ❌

---

## Validation Checklist

**Before Committing Helm Chart**:
- [ ] `helm lint ./helm/` passes with zero errors
- [ ] `helm template taskflow ./helm/ -f ./helm/values-dev.yaml` renders valid YAML
- [ ] All required values present in values.yaml
- [ ] No real secret values in any file
- [ ] Chart.yaml has all required fields
- [ ] NOTES.txt provides clear post-install instructions
- [ ] values-dev.yaml overrides make sense for Minikube

**Before Deployment**:
- [ ] Docker images built and tagged correctly
- [ ] Images loaded into Minikube (`minikube image load`)
- [ ] Secrets created manually (`kubectl create secret`)
- [ ] Helm install succeeds without errors
- [ ] Pods reach Running state within 30 seconds
- [ ] Services accessible via port-forward
- [ ] Application functionality verified

---

## Change Management

**When to Update Helm Contracts**:
- New configuration value needed
- New optional feature (ingress, monitoring)
- Resource limit changes
- New environment variable
- Breaking change to values schema

**Amendment Process**:
1. Update this contract document
2. Update Chart.yaml, values.yaml, templates as needed
3. Increment chart version appropriately
4. Run `helm lint` to validate
5. Test in Minikube
6. Document in plan.md
