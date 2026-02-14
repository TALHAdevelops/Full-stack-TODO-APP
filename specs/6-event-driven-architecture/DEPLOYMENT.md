# TaskFlow Phase 5 - Kubernetes Deployment Guide

## Overview

This guide covers deploying TaskFlow's event-driven architecture on a Civo Kubernetes cluster using Helm and Dapr.

---

## 1. Civo Cluster Setup

### Prerequisites
- [Civo CLI](https://www.civo.com/docs/overview/civo-cli) installed
- Civo account with free credit ($250 for new accounts)
- `kubectl` installed
- `helm` installed

### Create the Cluster

```bash
# Authenticate with Civo
civo apikey save taskflow-key <YOUR_API_KEY>
civo region use NYC1

# Create a 2-node cluster (small nodes for free-tier budget)
civo kubernetes create taskflow-cluster \
  --size g4s.kube.small \
  --nodes 2 \
  --wait

# Save kubeconfig
civo kubernetes config taskflow-cluster --save --merge

# Verify connection
kubectl get nodes
```

### Create Namespace

```bash
kubectl create namespace taskflow
kubectl config set-context --current --namespace=taskflow
```

---

## 2. Dapr Installation on Kubernetes

### Install Dapr CLI

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash

# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Verify
dapr --version
```

### Initialize Dapr on the Cluster

```bash
# Install Dapr into the cluster
dapr init -k --wait

# Verify Dapr system pods are running
kubectl get pods -n dapr-system

# Expected output:
# dapr-operator-xxx          Running
# dapr-sentry-xxx            Running
# dapr-placement-server-xxx  Running
# dapr-sidecar-injector-xxx  Running
# dapr-dashboard-xxx         Running
```

### Apply Dapr Components

The Dapr component manifests are in `k8s/dapr/`:

```bash
# Apply Kafka pubsub component
kubectl apply -f k8s/dapr/pubsub.yaml -n taskflow

# Apply Redis state store component
kubectl apply -f k8s/dapr/statestore.yaml -n taskflow

# Apply cron binding for scheduled tasks
kubectl apply -f k8s/dapr/cron-binding.yaml -n taskflow

# Verify components
dapr components -k -n taskflow
```

---

## 3. Helm Deployment

### Step 1: Create Secrets

Before deploying, create the required Kubernetes secrets:

```bash
kubectl create secret generic taskflow-secrets \
  --from-literal=DATABASE_URL='postgresql://user:pass@host/dbname?sslmode=require' \
  --from-literal=BETTER_AUTH_SECRET='your-secret-key-minimum-32-characters-long' \
  --from-literal=KAFKA_SASL_USERNAME='taskflow-producer' \
  --from-literal=KAFKA_SASL_PASSWORD='your-kafka-password' \
  -n taskflow
```

### Step 2: Install with Helm

```bash
# From the project root directory

# Development (local Minikube)
helm install taskflow helm/ \
  -f helm/values-dev.yaml \
  -n taskflow

# Production (Civo cloud)
helm install taskflow helm/ \
  -f helm/values-prod.yaml \
  -n taskflow

# Verify deployment
kubectl get pods -n taskflow
kubectl get services -n taskflow
```

### Step 3: Verify Health

```bash
# Port-forward to test the backend health endpoint
kubectl port-forward svc/taskflow-backend 8000:8000 -n taskflow

# In another terminal
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"5.0.0"}
```

### Step 4: Upgrade / Rollback

```bash
# Upgrade after code changes
helm upgrade taskflow helm/ \
  -f helm/values-prod.yaml \
  -n taskflow

# Rollback to previous release
helm rollback taskflow 1 -n taskflow

# Check release history
helm history taskflow -n taskflow
```

---

## 4. Monitoring

### Check Logs

```bash
# Backend logs
kubectl logs -l app=taskflow-backend -n taskflow -f

# Dapr sidecar logs
kubectl logs -l app=taskflow-backend -n taskflow -c daprd -f

# Redpanda logs (if in-cluster)
kubectl logs -l app=redpanda -n taskflow -f
```

### Dapr Dashboard

```bash
dapr dashboard -k -n taskflow
# Opens browser at http://localhost:8080
```

---

## 5. Teardown

```bash
# Uninstall Helm release
helm uninstall taskflow -n taskflow

# Remove Dapr
dapr uninstall -k

# Delete the Civo cluster (stops billing)
civo kubernetes delete taskflow-cluster --yes
```
