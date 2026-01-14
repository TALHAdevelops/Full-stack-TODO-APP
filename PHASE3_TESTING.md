# TaskFlow Phase III - Testing & Deployment Guide

**Status**: Ready for Testing
**Last Updated**: 2026-01-13
**Implementation**: 33/37 tasks completed

---

## Quick Start

### Backend Setup

1. **Ensure models are registered** (already done in T-301/T-302):
   ```bash
   cd backend
   python -c "from models import Conversation, Message; print('Models loaded successfully')"
   ```

2. **Run backend server**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
   - Backend available at: `http://localhost:8000`
   - API docs at: `http://localhost:8000/docs`

3. **Verify database tables are created**:
   - Tables: `users`, `tasks`, `conversations`, `messages`
   - On first request, SQLModel will create all tables via `create_db_and_tables()`

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Set environment variables** in `frontend/.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXTAUTH_SECRET=your-secret-here
   NEXTAUTH_URL=http://localhost:3000
   ```

3. **Run frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   - Frontend available at: `http://localhost:3000`

---

## Manual Testing (T-327 & T-334)

### Test User Story 1: Add Task via Natural Language

**Setup**:
1. Navigate to `http://localhost:3000`
2. Sign up or log in
3. Navigate to `/chat`

**Test Case 1.1**:
```
User: "Add buy milk"
Expected:
- Agent responds: "I've created the task 'buy milk' for you (ID: X)"
- Task appears in dashboard
- Tool calls show: ✓ add_task executed
```

**Test Case 1.2**:
```
User: "Remember to call the plumber tomorrow"
Expected:
- Agent creates task with title "call the plumber tomorrow"
- Confirmation includes task ID
```

**Test Case 1.3 (Clarification)**:
```
User: "Add milk and bread"
Expected:
- Agent asks: "Do you want to create one task 'milk and bread' or two separate tasks?"
- Agent waits for clarification
```

### Test User Story 2: List Tasks via Chat

**Test Case 2.1**:
```
Setup: Create 2 pending tasks and 1 completed task

User: "Show pending tasks"
Expected:
- Agent lists 2 pending tasks with ID, title, completed status
- Format: "○ Task 1: buy milk", "○ Task 2: call plumber"
```

**Test Case 2.2**:
```
User: "What do I need to do?"
Expected:
- Same as 2.1 (agent understands natural language variation)
```

**Test Case 2.3**:
```
User: "Show completed tasks"
Expected:
- Agent lists only the 1 completed task
- Format: "✓ Task 3: ..."
```

### Test User Story 3: Complete Task via Chat

**Test Case 3.1**:
```
Setup: Have task ID 1 titled "buy milk"

User: "Mark task 1 done"
Expected:
- Agent: "I've marked task 1 as complete. Nice work!"
- Task 1 now shows as completed in dashboard
```

**Test Case 3.2**:
```
User: "Complete the milk task"
Expected:
- Agent finds task by partial name
- Task marked as complete
```

**Test Case 3.3 (Already Completed)**:
```
Setup: Task is already completed

User: "Mark task 1 done"
Expected:
- Agent: "Task 1 is already completed"
- No error, graceful handling
```

### Test User Story 4: Update Task via Chat

**Test Case 4.1**:
```
Setup: Have task ID 1 "buy milk"

User: "Change task 1 to 'buy milk and bread'"
Expected:
- Agent: "I've updated task 1 to 'buy milk and bread'"
- Dashboard reflects new title
```

**Test Case 4.2**:
```
User: "Update that task"
Expected:
- Agent asks: "Which task? Please provide task ID or name"
- Handles ambiguous reference
```

### Test User Story 5: Delete Task via Chat

**Test Case 5.1**:
```
Setup: Have task ID 2

User: "Delete task 2"
Expected:
- Agent asks: "Are you sure? This will permanently remove task 2? Please respond with 'Yes' to confirm."
- User responds: "Yes"
- Agent: "I've permanently deleted task 2"
- Task 2 removed from dashboard
```

**Test Case 5.2 (Nonexistent Task)**:
```
User: "Delete task 999"
Expected:
- Agent: "Task 999 not found"
- No error thrown
```

### Test User Story 6: Handle Ambiguous Input

**Test Case 6.1**:
```
User: "Add milk and complete the shopping list"
Expected:
- Agent detects ambiguity
- Agent asks: "Do you want to: (1) create a task..., or (2) add a task and complete another?"
```

**Test Case 6.2**:
```
User: "Show me"
Expected:
- Agent asks: "Would you like to see your pending tasks, completed tasks, or all tasks?"
```

---

## API Testing (Manual with curl or Postman)

### 1. Get Auth Token

```bash
# Sign up
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 2. Test Chat Endpoint

```bash
# Create a new chat conversation
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add buy milk"}'

# Continue conversation
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"{conv_id}","message":"Show pending tasks"}'
```

### 3. Test Conversation History

```bash
# List conversations
curl -X GET http://localhost:8000/api/{user_id}/conversations \
  -H "Authorization: Bearer {token}"

# Get conversation history
curl -X GET http://localhost:8000/api/{user_id}/conversations/{conv_id} \
  -H "Authorization: Bearer {token}"
```

### 4. Test MCP Tools Directly (Python)

```python
from backend.mcp_server import invoke_tool

# Test add_task
result = invoke_tool("add_task", user_id="user123", title="Buy milk")
print(result)

# Test list_tasks
result = invoke_tool("list_tasks", user_id="user123", filter="pending")
print(result)

# Test complete_task
result = invoke_tool("complete_task", user_id="user123", task_id=1)
print(result)
```

---

## Error Handling Tests

### T-326 - Graceful Error Handling

**Test 6.1: Invalid JWT**
```bash
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Authorization: Bearer invalid-token" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add task"}'

Expected: 401 Unauthorized
```

**Test 6.2: User ID Mismatch**
```bash
# Token for user123, but request for user456
curl -X POST http://localhost:8000/api/user456/chat \
  -H "Authorization: Bearer {token_for_user123}" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add task"}'

Expected: 403 Forbidden
```

**Test 6.3: Empty Message**
```bash
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"message":""}'

Expected: 400 Bad Request - "Message cannot be empty"
```

**Test 6.4: Message Too Long**
```bash
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"$(printf 'A%.0s' {1..5001})\"}"

Expected: 400 Bad Request - "Message exceeds 5000 character limit"
```

**Test 6.5: Conversation Not Found**
```bash
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"invalid-uuid","message":"test"}'

Expected: 404 Not Found - "Conversation not found"
```

---

## Performance Testing (T-335)

### Response Time Goals

- Chat endpoint response: **< 2 seconds**
- MCP tool execution: **< 500ms**
- Message list load: **< 100ms**
- Frontend load: **< 1 second**

### Test Script

```bash
# Time a chat request
time curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add task"}'
```

---

## Security Testing (T-336)

### SQL Injection Test
```bash
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add '\'' OR 1=1 --"}'

Expected: Task created with title "Add '' OR 1=1 --" (sanitized)
```

### XSS Test
```bash
curl -X POST http://localhost:8000/api/user123/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add <script>alert(1)</script>"}'

Expected: Task created, script properly escaped in frontend
```

### User Isolation Test
```bash
# As user1, try to access user2's conversation
curl -X GET http://localhost:8000/api/user1/conversations/user2_conv_id \
  -H "Authorization: Bearer {user1_token}"

Expected: 404 Not Found (user1 cannot see user2's conversations)
```

---

## Deployment (T-337)

### Backend Deployment (Railway/AWS)

1. **Set environment variables**:
   ```
   DATABASE_URL=postgresql://...neon...
   NEXTAUTH_SECRET=...
   BETTER_AUTH_SECRET=...
   ```

2. **Deploy**:
   ```bash
   git push heroku main  # or Railway equivalent
   ```

3. **Verify**:
   ```bash
   curl https://your-api.railway.app/docs
   ```

### Frontend Deployment (Vercel)

1. **Update API_URL** in `frontend/lib/api/chat-client.ts`:
   ```typescript
   const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-api.railway.app'
   ```

2. **Deploy**:
   ```bash
   git push origin main
   ```
   (Vercel auto-deploys on push)

3. **Verify**:
   ```bash
   curl https://your-frontend.vercel.app/chat
   ```

### Health Check

```bash
# Backend health
curl https://your-api.railway.app/

# Frontend health
curl https://your-frontend.vercel.app/

# Chat endpoint
curl -X POST https://your-api.railway.app/api/{user_id}/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

---

## Known Limitations & Future Work

### Not Implemented in Phase III MVP

- T-327: Manual testing pending (no automated tests)
- Delete conversation endpoint (delete UI button exists but endpoint not created)
- Conversation title editing
- Real-time WebSocket updates (uses polling instead)
- Conversation search/filtering
- Message editing/deletion
- Typing indicators

### Phase IV Enhancements

- Advanced NLP (intent detection via Claude API)
- Multi-step conversations with context
- Task due dates and reminders via chat
- Recurring tasks
- Task subtasks and dependencies
- Scheduled messages
- Integration with calendar
- Voice/speech input

---

## Troubleshooting

### Backend won't start

```bash
# Check dependencies
pip install -r requirements.txt

# Check database connection
python -c "from db import engine; print(engine)"
```

### Frontend shows "API is down"

```bash
# Verify backend is running
curl http://localhost:8000/docs

# Check NEXT_PUBLIC_API_URL in .env.local
echo $NEXT_PUBLIC_API_URL
```

### Chat not responding

```bash
# Check logs in backend terminal
# Look for: "Agent:" lines to see what intent was detected

# Test MCP tools directly
python -c "from mcp_server import invoke_tool; print(invoke_tool('list_tasks', user_id='test'))"
```

### Database errors

```bash
# Check if tables were created
python -c "from sqlmodel import SQLModel; from db import engine; SQLModel.metadata.create_all(engine); print('Tables created')"
```

---

## Test Results

| Test Category | Status | Notes |
|---------------|--------|-------|
| T-327: Chat Flow | ⏳ Pending | Requires manual testing with browser |
| T-334: Integration Tests | ⏳ Pending | All 6 user stories need testing |
| T-335: Performance | ⏳ Pending | Needs load testing |
| T-336: Security | ⏳ Pending | Needs security audit |
| T-337: Deployment | ⏳ Pending | Ready to deploy after testing |

---

**Next Steps**:
1. Run manual tests from this guide (T-327, T-334)
2. Performance testing (T-335)
3. Security audit (T-336)
4. Deploy to production (T-337)
