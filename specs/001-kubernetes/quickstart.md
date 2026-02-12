# Quickstart Guide - Phase IV Kubernetes Deployment

**Date**: 2026-02-07
**Audience**: Developers deploying TaskFlow to local Minikube for the first time
**Time to Complete**: 15-20 minutes

## Prerequisites

Before starting, ensure you have the following installed:

### Required Tools
```bash
# Verify installations
docker --version          # Docker 24.0+
minikube version          # Minikube 1.32+
kubectl version --client  # kubectl 1.28+
helm version              # Helm 3.14+
```

### Install Missing Tools

**Docker Desktop** (Windows/Mac):
- Download from https://www.docker.com/products/docker-desktop

**Minikube**:
```bash
# macOS
brew install minikube

# Windows (Chocolatey)
choco install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**kubectl**:
```bash
# macOS
brew install kubectl

# Windows (Chocolatey)
choco install kubernetes-cli

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

**Helm**:
```bash
# macOS
brew install helm

# Windows (Chocolatey)
choco install kubernetes-helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Required Credentials
- **Neon Database URL**: Obtain from https://neon.tech (from Phase III deployment)
- **Better Auth Secret**: 32-character random string (from Phase III .env)
- **OpenAI API Key**: Obtain from https://platform.openai.com (from Phase III .env)

---

## Step 1: Start Minikube Cluster

```bash
# Start Minikube with recommended resources
minikube start --memory=4096 --cpus=2

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

**Expected Output**:
```
Kubernetes control plane is running at https://127.0.0.1:xxxxx
minikube     Ready    control-plane   1m    v1.28.x
```

**Troubleshooting**:
- If Minikube fails to start, try: `minikube delete && minikube start`
- On Windows, ensure Hyper-V or WSL2 backend is enabled

---

## Step 2: Build Docker Images

```bash
# Navigate to repository root
cd /path/to/TALHA-HTFA

# Build frontend image
docker build -t taskflow-frontend:1.0.0 ./frontend

# Build backend image
docker build -t taskflow-backend:1.0.0 ./backend

# Verify images
docker images | grep taskflow
```

**Expected Output**:
```
taskflow-frontend    1.0.0    <image-id>    <size>    <time>
taskflow-backend     1.0.0    <image-id>    <size>    <time>
```

**Size Verification**:
- Frontend: Should be <200MB
- Backend: Should be <300MB
- If larger, review Dockerfile multi-stage builds

---

## Step 3: Load Images into Minikube

```bash
# Load frontend image
minikube image load taskflow-frontend:1.0.0

# Load backend image
minikube image load taskflow-backend:1.0.0

# Verify images are in Minikube
minikube image ls | grep taskflow
```

**Expected Output**:
```
docker.io/library/taskflow-frontend:1.0.0
docker.io/library/taskflow-backend:1.0.0
```

**Note**: This step is specific to Minikube. In cloud deployments, images are pulled from a container registry (Docker Hub, GCR, ECR).

---

## Step 4: Create Kubernetes Secrets

**CRITICAL**: Replace placeholders with your actual credentials.

```bash
# Create secrets (DO NOT commit these values to git!)
kubectl create secret generic taskflow-secrets \
  --from-literal=database-url='postgresql://user:password@host.region.neon.tech/dbname?sslmode=require' \
  --from-literal=better-auth-secret='your-32-character-random-secret-here' \
  --from-literal=openai-api-key='sk-your-openai-api-key-here'

# Verify secret was created
kubectl get secret taskflow-secrets
```

**Expected Output**:
```
NAME               TYPE     DATA   AGE
taskflow-secrets   Opaque   3      10s
```

**Finding Your Credentials**:
- **DATABASE_URL**: Check `backend/.env` from Phase III or Neon dashboard
- **BETTER_AUTH_SECRET**: Check `frontend/.env.local` from Phase III (BETTER_AUTH_SECRET variable)
- **OPENAI_API_KEY**: Check `backend/.env` from Phase III or OpenAI dashboard

---

## Step 5: Deploy with Helm

```bash
# Install TaskFlow Helm chart
helm install taskflow ./helm/ -f ./helm/values-dev.yaml

# Watch pods start up
kubectl get pods -w
```

**Expected Output** (after ~30 seconds):
```
NAME                                 READY   STATUS    RESTARTS   AGE
taskflow-backend-xxxxxxxxxx-xxxxx    1/1     Running   0          30s
taskflow-frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

**Troubleshooting**:
- If pods stuck in `ImagePullBackOff`: Images not loaded into Minikube (repeat Step 3)
- If pods stuck in `CrashLoopBackOff`: Check logs with `kubectl logs <pod-name>`
- If pods stuck in `Pending`: Insufficient cluster resources (check `kubectl describe pod <pod-name>`)

---

## Step 6: Access the Application

### Option A: Port Forward (Recommended)

```bash
# Forward frontend port in one terminal
kubectl port-forward svc/taskflow-frontend 3000:80

# Forward backend port in another terminal (optional, for API docs)
kubectl port-forward svc/taskflow-backend 8000:8000
```

**Access URLs**:
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs

### Option B: Minikube Service

```bash
# Open frontend in browser
minikube service taskflow-frontend

# Get service URL without opening browser
minikube service taskflow-frontend --url
```

---

## Step 7: Verify Deployment

### Test 1: Frontend Loads
1. Navigate to http://localhost:3000
2. You should see the TaskFlow login page
3. ✅ **Success**: Page loads without errors

### Test 2: Backend Health Check
```bash
# Test backend health endpoint
curl http://localhost:8000/health
```
**Expected Response**: `{"status":"healthy"}`

### Test 3: Sign Up New User
1. Click "Sign Up" on frontend
2. Enter email and password
3. Submit form
4. ✅ **Success**: User created, redirected to dashboard

### Test 4: Create Task
1. Sign in with test user
2. Click "Add Task" button
3. Enter task title and description
4. Submit form
5. ✅ **Success**: Task appears in task list

### Test 5: AI Chatbot
1. Click "Chat" button on dashboard
2. Type: "Create a task to buy groceries"
3. ✅ **Success**: Chatbot creates task and confirms

---

## Step 8: Inspect Resources

### View All Resources
```bash
kubectl get all -l app=taskflow
```

**Expected Output**:
```
NAME                                     READY   STATUS    RESTARTS   AGE
pod/taskflow-backend-xxxxxxxxxx-xxxxx    1/1     Running   0          5m
pod/taskflow-frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          5m

NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
service/taskflow-backend    ClusterIP   10.96.xxx.xxx   <none>        8000/TCP   5m
service/taskflow-frontend   NodePort    10.96.xxx.xxx   <none>        80:xxxxx   5m

NAME                                READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/taskflow-backend    1/1     1            1           5m
deployment.apps/taskflow-frontend   1/1     1            1           5m
```

### View Pod Logs
```bash
# Frontend logs
kubectl logs -l app=taskflow,component=frontend --tail=50

# Backend logs
kubectl logs -l app=taskflow,component=backend --tail=50
```

### View ConfigMap and Secrets
```bash
# View ConfigMap (non-sensitive config)
kubectl get configmap taskflow-config -o yaml

# View Secret (keys only, not values)
kubectl get secret taskflow-secrets -o jsonpath='{.data}' | jq 'keys'
```

---

## Scaling the Application

### Scale Up to 3 Replicas
```bash
# Update values file or use kubectl
kubectl scale deployment taskflow-frontend --replicas=3
kubectl scale deployment taskflow-backend --replicas=3

# Verify scaling
kubectl get pods -l app=taskflow
```

**Expected Output**:
```
NAME                                 READY   STATUS    RESTARTS   AGE
taskflow-backend-xxxxxxxxxx-xxxxx    1/1     Running   0          2m
taskflow-backend-xxxxxxxxxx-yyyyy    1/1     Running   0          10s
taskflow-backend-xxxxxxxxxx-zzzzz    1/1     Running   0          10s
taskflow-frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
taskflow-frontend-xxxxxxxxxx-yyyyy   1/1     Running   0          10s
taskflow-frontend-xxxxxxxxxx-zzzzz   1/1     Running   0          10s
```

### Scale Down to 1 Replica
```bash
kubectl scale deployment taskflow-frontend --replicas=1
kubectl scale deployment taskflow-backend --replicas=1
```

---

## Cleanup

### Uninstall TaskFlow
```bash
# Remove Helm release
helm uninstall taskflow

# Verify all resources deleted
kubectl get all -l app=taskflow
```

**Expected Output**: `No resources found in default namespace.`

### Delete Secrets (Optional)
```bash
# Manually delete secrets if needed
kubectl delete secret taskflow-secrets
```

### Stop Minikube
```bash
# Stop cluster (keeps data)
minikube stop

# Delete cluster (removes all data)
minikube delete
```

---

## Common Issues

### Issue: Pods stuck in Pending
**Cause**: Insufficient cluster resources
**Solution**:
```bash
minikube delete
minikube start --memory=6144 --cpus=4
```

### Issue: ImagePullBackOff
**Cause**: Images not loaded into Minikube
**Solution**:
```bash
minikube image load taskflow-frontend:1.0.0
minikube image load taskflow-backend:1.0.0
```

### Issue: CrashLoopBackOff on Backend
**Cause**: Invalid DATABASE_URL or missing secret
**Solution**:
```bash
# Check backend logs
kubectl logs -l component=backend --tail=50

# Verify secret exists
kubectl get secret taskflow-secrets

# Recreate secret with correct values
kubectl delete secret taskflow-secrets
kubectl create secret generic taskflow-secrets --from-literal=...
```

### Issue: Frontend can't reach backend
**Cause**: Service DNS not resolving or BACKEND_URL misconfigured
**Solution**:
```bash
# Verify services exist
kubectl get svc

# Check frontend logs for connection errors
kubectl logs -l component=frontend --tail=50

# Verify ConfigMap has correct BACKEND_URL
kubectl get configmap taskflow-config -o yaml | grep BACKEND_URL
```

### Issue: 503 Service Unavailable on /health
**Cause**: Backend can't connect to Neon database
**Solution**:
- Verify DATABASE_URL is correct (check for typos, SSL parameters)
- Ensure your IP is whitelisted in Neon dashboard
- Test database connection locally: `psql <DATABASE_URL>`

---

## Next Steps

- **Production Deployment**: Adapt Helm chart for cloud Kubernetes (GKE, EKS, AKS)
- **CI/CD Pipeline**: Automate Docker builds and Helm deployments
- **Monitoring**: Add Prometheus and Grafana for observability
- **Ingress**: Configure ingress controller for external access without port-forward
- **Autoscaling**: Implement Horizontal Pod Autoscaler based on CPU/memory

---

## Additional Resources

- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Helm Documentation**: https://helm.sh/docs/
- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/
- **Docker Documentation**: https://docs.docker.com/
- **Neon Documentation**: https://neon.tech/docs/

---

**Congratulations!** 🎉 You've successfully deployed TaskFlow to Kubernetes. All Phase III features (signup, signin, tasks, chatbot) now run in a containerized, orchestrated environment.
