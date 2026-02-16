---
id: PHR-001
title: Phase 5 Event-Driven Architecture Deployment
stage: green
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: 6-event-driven-architecture
branch: main
user: TALHAdevelops
command: /sp.phr
labels: ["deployment", "vercel", "neon", "cors", "github", "event-driven", "phase5"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/main.py
  - render.yaml
  - .gitignore
  - frontend/vercel.json
  - DEPLOY.md
  - backend/.env (created, gitignored)
  - .env (created, gitignored)
tests:
  - Health endpoint: GET /health → 200 {"status":"healthy","version":"5.0.0"}
  - Auth middleware: GET /api/tasks/recurring → 401 Not authenticated
  - CORS preflight: Access-Control-Allow-Origin header verified
  - Swagger docs: GET /docs → 200
  - Frontend page load: GET / → 200
---

## Prompt

Record the full Phase 5 deployment session: pushed 70-file Phase 5 Event-Driven Architecture to GitHub, fixed security issue (removed .env with credentials from git tracking), removed 11,217 accidentally committed node_modules files, applied 3 database migrations to Neon PostgreSQL (recurring task fields, reminders table, event_log table), deployed frontend to Vercel (Next.js) and backend to Vercel (FastAPI serverless), configured CORS/env vars/SSO protection, verified end-to-end connectivity. All services live at $0/month on free tiers. Frontend: https://taskflow-frontend-muhammad-talhas-projects-d748a6fc.vercel.app Backend: https://taskflow-backend-muhammad-talhas-projects-d748a6fc.vercel.app

## Response snapshot

Completed full deployment pipeline: pushed Phase 5 to GitHub (70 files, 7503 insertions), applied 3 Neon DB migrations, fixed critical security issues (.env leaked to git, 11K node_modules tracked), deployed both frontend (Next.js) and backend (FastAPI) to Vercel via API, configured CORS origins, environment variables, and disabled SSO protection. Both services verified live and communicating at $0/month.

## Outcome

- ✅ Impact: Full-stack application deployed to production with event-driven architecture (Kafka-ready), real-time WebSocket endpoints, recurring tasks, reminders system, and audit trail. Both frontend and backend live on Vercel free tier with Neon PostgreSQL.
- 🧪 Tests: Manual endpoint verification — health check (200), auth middleware (401/403), CORS headers (Access-Control-Allow-Origin correct), Swagger docs (200), frontend page load (200). Backend loads all 30 routes successfully.
- 📁 Files: 5 files modified/created in deployment commits: backend/main.py (CORS fix), render.yaml (free tier config), .gitignore (root node_modules + .env), frontend/vercel.json (installCommand), DEPLOY.md (deployment guide). Additionally removed 11,220 tracked node_modules files and root package-lock.json from git.
- 🔁 Next prompts: (1) Set up Render deployment as alternative backend host with WebSocket support, (2) Configure Redpanda Cloud Serverless for production Kafka, (3) Set up Civo Kubernetes cluster for Cloud K8s deployment option, (4) Add CI/CD GitHub Actions workflow, (5) Restart Docker Desktop and test docker-compose local deployment.
- 🧠 Reflection: The biggest deployment blocker was discovering 11,217 node_modules files accidentally committed to git — this caused Vercel's first deployment to fail with EACCESS (exit code 126). Always verify .gitignore covers root-level node_modules, not just frontend/node_modules. Also, the root .env with database credentials was tracked in git — a critical security issue caught and fixed mid-deployment. Vercel CLI's non-interactive mode had persistent --scope issues; using the Vercel REST API directly with urllib proved far more reliable for automated deployments.

## Evaluation notes (flywheel)

- Failure modes observed: (1) Root .env with production credentials was committed to git — caught during deployment and removed. (2) Root node_modules (11K files) were tracked, causing Vercel build failure with EACCESS error. (3) Vercel CLI --scope flag broken in non-interactive mode — had to fall back to REST API. (4) Docker Desktop engine returning 500 errors — could not test docker-compose locally. (5) First Vercel deployment had SSO protection enabled by default, returning 401 on all requests.
- Graders run and results (PASS/FAIL): Manual verification — PASS (health 200, auth 401, CORS headers correct, frontend 200, Swagger 200)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add a pre-deployment checklist that verifies .gitignore covers root-level artifacts (node_modules, .env, package-lock.json) before any push to prevent credential leaks and bloated repos.
