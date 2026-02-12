---
id: PHR-001
title: Phase IV Kubernetes Constitution
stage: constitution
date: 2026-02-06
surface: claude-code
model: claude-opus-4-5-20251101
feature: phase-iv-k8s-deployment
branch: main
user: developer
command: /sp.constitution
labels: [kubernetes, minikube, helm, docker, infrastructure, phase-iv]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - path: .specify/memory/constitution.md
    action: updated
tests:
  - null
---

## Prompt

Generate Constitution for Phase IV (Local Kubernetes Deployment on Minikube)

CONTEXT:
- Phase II: Multi-user todo web app (Next.js 16+, FastAPI, SQLModel, Neon, Better Auth)
- Phase III: Added AI chatbot with OpenAI Agents SDK, MCP SDK, conversational interface
- Phase IV NOW: Deploy everything to Kubernetes (locally on Minikube)
- Folder Structure: Using Spec-Kit Plus (.specify/ folder)

REQUIREMENTS:
1. Extend Core Principles from Phase II & III, add K8s-specific ones (Container-First Design, Kubernetes-Native Patterns, Infrastructure as Code, Helm Standards)
2. Define Architectural Constraints for Phase IV (containerization, K8s-native design, Helm standards, stateless containers, resource management)
3. Define Coding Standards for Phase IV (Dockerfile standards, Helm chart standards, K8s manifest standards, configuration management)
4. Define Security Rules for Phase IV (secrets management, container security, image versioning)
5. Define Performance Expectations for Phase IV (pod startup time, deployment rollout, resource efficiency, horizontal scaling)
6. Define Testing Requirements for Phase IV (Dockerfile validation, image size limits, Helm lint, K8s deployment testing)
7. Define Non-Negotiables for Phase IV

## Response snapshot

Created Phase IV constitution extending Phase II + III with 4 new core principles:
- XIII. Container-First Design: Multi-stage builds, minimal base images, stateless containers
- XIV. Kubernetes-Native Patterns: Deployments over Pods, Services, ConfigMaps/Secrets, health probes, resource management
- XV. Infrastructure as Code: Declarative config, reproducible deployments, GitOps ready
- XVI. Helm Standards: Helm as package manager, values-driven configuration, templated manifests

Added comprehensive sections:
- Infrastructure Stack (Minikube, Helm 3, kubectl, Docker)
- Architectural Constraints (container requirements, K8s design, resource boundaries, external dependencies)
- Coding Standards (Dockerfile, Helm chart, K8s manifest standards with examples)
- Security Rules (K8s secrets, container security, network security)
- Performance Expectations (container/K8s performance, resource efficiency, scaling)
- Testing Requirements (Dockerfile validation, image size limits, Helm lint, K8s deployment tests)
- Non-Negotiables (MUST Have / MUST NOT Have for Phase IV)
- Deployment Standards (Minikube workflow, project structure)

Version bumped: 2.0.0 → 3.0.0 (MAJOR: new deployment paradigm)

## Outcome

- ✅ Impact: High - Establishes complete governance framework for Phase IV K8s deployment
- 🧪 Tests: N/A (constitution document)
- 📁 Files: 1 updated (.specify/memory/constitution.md)
- 🔁 Next prompts: /sp.specify (create Phase IV feature spec), /sp.plan (create implementation plan)
- 🧠 Reflection: Constitution comprehensively covers all K8s deployment aspects while maintaining continuity with Phase II/III principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
