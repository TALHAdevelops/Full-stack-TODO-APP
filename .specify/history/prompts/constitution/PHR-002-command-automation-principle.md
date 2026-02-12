---
id: PHR-002
title: Command Automation Principle Addition
stage: constitution
date: 2026-02-08
surface: claude-code
model: claude-opus-4-5-20251101
feature: phase-iv-k8s-deployment
branch: 001-kubernetes
user: developer
command: /sp.constitution
labels: [kubernetes, automation, claude-code, command-execution, phase-iv]
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

Generate Constitution for Phase IV (Local Kubernetes Deployment on Minikube) with emphasis on Command Automation.

Key requirements:
- Claude Code executes ALL commands (docker build, helm install, kubectl, etc.)
- No manual command entry required from user
- Add Command Automation as a new core principle (XVII)
- Define automation standards and execution patterns

## Response snapshot

Updated Phase IV constitution from v3.0.0 to v3.1.0 with:

**New Principle XVII - Command Automation:**
- AI-Executed Infrastructure: Claude Code runs all docker, helm, kubectl, minikube commands
- No Manual Command Entry: User doesn't copy-paste commands
- Scripted Operations: Common patterns for consistent execution
- Error Handling: Claude Code diagnoses and handles failures
- Progress Reporting: Clear feedback on command status
- Idempotent Execution: Commands safe to re-run

**New Section - Command Automation Standards:**
- Automated Command Categories (docker, minikube, helm, kubectl)
- Execution Patterns (sequential with verification, helm deployment, port-forward)
- Command Output Handling (success, failure, long-running, interactive)
- User Involvement (secrets only, browser testing, approval gates)

## Outcome

- ✅ Impact: MINOR - Added Principle XVII and Command Automation Standards section
- 🧪 Tests: N/A - constitution document
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: /sp.specify, /sp.plan, /sp.tasks for Phase IV implementation
- 🧠 Reflection: User explicitly required command automation principle; this was missing from v3.0.0 and was a key Phase IV requirement

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify templates pending updates are addressed in next planning session
