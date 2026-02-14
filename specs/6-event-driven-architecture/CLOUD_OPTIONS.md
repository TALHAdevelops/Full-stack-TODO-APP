# TaskFlow Phase 5 - Cloud Deployment Options

## Deployment Options Comparison

| Feature              | Local (Docker Compose) | Cloud Simple (Render + Vercel) | Cloud K8s (Civo + Helm) |
|----------------------|------------------------|-------------------------------|-------------------------|
| **Backend**          | Docker container       | Render.com Web Service        | Civo K8s Pod            |
| **Frontend**         | Docker container       | Vercel (Next.js)              | Civo K8s Pod            |
| **Kafka/Redpanda**   | Local Redpanda         | Redpanda Cloud Serverless     | Redpanda in-cluster     |
| **Database**         | Local PostgreSQL       | Neon / Supabase (free tier)   | Civo managed DB         |
| **Redis**            | Local Redis            | Upstash Redis (free tier)     | Redis in-cluster        |
| **WebSocket**        | Direct                 | Render native WS              | Ingress WS              |
| **Dapr**             | Optional               | Disabled                      | Dapr sidecar            |
| **SSL/TLS**          | Self-signed            | Automatic                     | cert-manager            |
| **Cost**             | $0                     | $0                            | $0                      |

## Cost Breakdown

All three options are designed to run at **$0/month** using free tiers:

### Local (Docker Compose) - $0
- Everything runs on your machine
- No cloud accounts needed
- Best for development and testing

### Cloud Simple (Render + Vercel) - $0
- **Render.com**: Free tier includes 750 hours/month for web services
- **Vercel**: Free tier for hobby/personal Next.js deployments
- **Redpanda Cloud Serverless**: Free tier includes 1 GB transfer/month
- **Neon PostgreSQL**: Free tier includes 0.5 GB storage
- **Upstash Redis**: Free tier includes 10,000 commands/day

### Cloud K8s (Civo) - $0
- **Civo**: $250 free credit for new accounts (lasts months for small clusters)
- All services run in-cluster (Redpanda, Redis, PostgreSQL)
- Best for learning Kubernetes and Helm

## Redpanda Cloud Serverless Setup

### Step 1: Sign Up
1. Go to [cloud.redpanda.com](https://cloud.redpanda.com)
2. Create a free account (GitHub/Google SSO available)

### Step 2: Create a Serverless Cluster
1. Click "Create Cluster"
2. Select **Serverless** tier (free)
3. Choose a region close to your Render deployment
4. Name it `taskflow-events`
5. Click "Create"

### Step 3: Get SASL Credentials
1. Navigate to your cluster dashboard
2. Go to **Security** > **ACLs**
3. Create a new user:
   - Username: `taskflow-producer`
   - Mechanism: `SCRAM-SHA-256`
   - Save the generated password
4. Create ACLs for your topics:
   - Topic: `task-events` - Allow produce and consume
   - Topic: `reminder-events` - Allow produce and consume

### Step 4: Get Bootstrap Server URL
1. Go to **Overview** tab
2. Copy the **Bootstrap Server** URL (looks like `seed-xxxxx.region.cloud.redpanda.com:9092`)

### Step 5: Configure Environment Variables
Set the following in your Render.com dashboard or Helm values:

```bash
KAFKA_BOOTSTRAP_SERVERS=seed-xxxxx.region.cloud.redpanda.com:9092
KAFKA_SASL_USERNAME=taskflow-producer
KAFKA_SASL_PASSWORD=<your-generated-password>
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=SCRAM-SHA-256
```
