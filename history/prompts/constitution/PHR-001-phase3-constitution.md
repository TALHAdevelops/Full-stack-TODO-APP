---
id: PHR-001
title: Phase III AI Chatbot Constitution
stage: constitution
date: 2026-01-12
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: TALHAdevelops
command: /sp.constitution
labels: ["constitution", "ai-chatbot", "mcp", "phase-iii", "governance", "architecture"]
links:
  spec: .specify/memory/constitution.md
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Generate a Constitution for Phase III: TaskFlow AI Chatbot that extends and builds on the Phase II Constitution.

Context:
- Phase II: Multi-user todo web app (Next.js 16+, FastAPI, Better Auth, SQLModel, Neon)
- Phase III Goal: Add AI-powered conversational interface using OpenAI Agents SDK + MCP

Requirements:

1. **Extend Phase II Core Principles** while adding new ones for AI/chatbot:
   - Keep: Security First, Type Safety, API-First, Modern Frontend, Database Best Practices, Code Quality
   - Add: Stateless Chat Architecture, MCP as Single Source of Truth, Agent Intent Routing, Conversation Persistence

2. **Define Architectural Constraints for AI**:
   - Chat endpoint is stateless (no session memory on server)
   - All task operations MUST go through MCP tools (no direct DB from chat endpoint)
   - Agent SDK handles routing; MCP tools handle execution
   - Conversation history stored in DB (new Conversation & Message tables)
   - MCP tools verify user_id before any DB access (user isolation continues from Phase II)

3. **Define Coding Standards for Phase III**:
   - Python: Type hints for all functions, error handling in MCP tools
   - TypeScript: No 'any' types in ChatKit integration
   - MCP tools follow same patterns as Phase II routes (Pydantic validation, user_id verification)
   - All responses logged to database

4. **Define Security Rules specific to Phase III**:
   - MCP tools verify user_id before DB access (inherit from Phase II)
   - Chat endpoint requires JWT auth (same as Phase II task endpoints)
   - Agent cannot access raw DB; only through MCP tools
   - Tool invocations logged with user_id, timestamp, result
   - Natural language input sanitized (no injection attacks via chat)

5. **Define Performance Expectations**:
   - Chat endpoint response: < 5 seconds (including agent execution)
   - MCP tool execution: < 2 seconds per tool
   - Agent decision time: < 1 second (intent routing)
   - Database queries optimized (indexes on user_id, conversation_id)

6. **Define Testing Requirements**:
   - Every MCP tool has unit tests
   - Agent behavior tested with 15+ sample conversations
   - Chat endpoint tested with JWT verification
   - End-to-end: user message → agent → tool → DB → response

## Response snapshot

Generated Phase III Constitution extending Phase II foundation by adding 4 new principles (IX-XII) focused on AI/MCP architecture, along with updated security rules, performance expectations, testing requirements, and data models for conversation persistence. Version bumped from 1.0.0 to 2.0.0 (MINOR) with comprehensive Sync Impact Report documenting all changes and flagging dependent template updates.

## Outcome

- ✅ Impact: Full Phase III Constitution created with 12 core principles (8 Phase II retained + 4 new), MCP tool standards section, updated API endpoints with chat route definitions, conversation/message data models, extended security requirements for tool invocation logging and user isolation, performance SLAs for chat (5s response, 2s per tool, 1s agent decision), testing requirements for MCP tools/agent behavior/E2E, and complete governance framework with semantic versioning policy
- 🧪 Tests: None (governance document; no code to test)
- 📁 Files: .specify/memory/constitution.md (updated from 1.0.0 to 2.0.0)
- 🔁 Next prompts: Update dependent spec/plan/tasks templates; update README with Phase III features; implement MCP tools following new standards; implement chat endpoint with agent integration
- 🧠 Reflection: Constitution successfully extends Phase II by maintaining backward compatibility while adding AI-specific governance; MCP as gatekeeper pattern ensures security through tool verification rather than endpoint logic

## Evaluation notes (flywheel)

- Failure modes observed: None; requirements were clear and comprehensive; template structure followed; all placeholders filled with concrete values from user requirements
- Graders run and results (PASS/FAIL): PASS - No unexplained bracket tokens remain; version bumped correctly (1.0.0→2.0.0 MINOR); dates in ISO format; principles declarative and testable; Sync Impact Report comprehensive; template dependencies identified
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): After implementation begins, run compliance check against constitution to verify MCP tools enforce user_id checks; add constitution amendment process doc to track future changes systematically
