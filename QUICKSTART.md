# TaskFlow Phase III - Quick Start Guide

Get the AI Chat application running in minutes.

---

## Prerequisites

- Python 3.9+ with pip
- Node.js 18+ with npm
- PostgreSQL database (or Neon)
- Git

---

## 1. Backend Setup (5 minutes)

### Clone/Navigate to backend
```bash
cd backend
```

### Install Python dependencies
```bash
pip install -r requirements.txt
```

### Configure environment
Create `.env` file (or update existing):
```env
DATABASE_URL=postgresql://user:password@localhost:5432/taskflow
NEXTAUTH_SECRET=your-secret-key-here
BETTER_AUTH_SECRET=another-secret-key-here
```

### Start backend
```bash
uvicorn main:app --reload
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Verify**:
- Open http://localhost:8000/docs
- You should see the API documentation

---

## 2. Frontend Setup (5 minutes)

### Open new terminal, navigate to frontend
```bash
cd frontend
```

### Install Node dependencies
```bash
npm install
```

### Configure environment
Create/update `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=your-secret-key-here
NEXTAUTH_URL=http://localhost:3000
```

### Start frontend
```bash
npm run dev
```

**Expected Output**:
```
> TaskFlow Frontend
> ▲ Next.js 16.0.0
> Local:        http://localhost:3000
```

**Verify**:
- Open http://localhost:3000
- You should see the login page

---

## 3. Test the Application (5 minutes)

### Create an account
1. Go to http://localhost:3000
2. Click "Sign Up"
3. Enter email and password
4. Click "Create Account"

### Navigate to chat
1. After login, click "Chat" in navigation
2. You should see the chat interface

### Test a message
1. In the chat input, type: "Add buy milk"
2. Press Enter
3. The agent should respond with confirmation

**Expected Response**:
```
✓ I've created the task 'buy milk' for you (ID: 1)
```

### Try more commands
```
"Show pending tasks"      → Lists all tasks
"Mark task 1 done"        → Completes task 1
"Change task 1 to buy groceries" → Updates task
"Delete task 1"           → Deletes with confirmation
```

---

## 4. View in Dashboard

1. Go to http://localhost:3000/dashboard
2. Your new task should appear in the task list
3. Tasks created via chat sync with dashboard

---

## Development Tips

### View Backend Logs
The backend terminal shows all requests and agent activity:
```
INFO:     Agent: user=..., intent=CREATE, message=Add buy milk
```

### View Database
Use any PostgreSQL client to connect to your database:
```bash
psql postgresql://user:password@localhost:5432/taskflow
```

Query conversations and messages:
```sql
SELECT * FROM conversations;
SELECT * FROM messages;
SELECT * FROM tasks;
```

### Debug Agent Intent
Edit `backend/agents.py` to add print statements:
```python
def parse_intent(message: str) -> str:
    print(f"DEBUG: Parsing message: {message}")
    # ... rest of code
```

### Hot Reload
Both backend and frontend support hot reload:
- Change backend code → auto-restarts (uvicorn --reload)
- Change frontend code → auto-refreshes in browser

---

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
pip install -r requirements.txt
```

**Error**: `Connection to postgres://... failed`
- Check DATABASE_URL is correct
- Verify PostgreSQL is running
- Create database if needed: `createdb taskflow`

### Frontend won't start

**Error**: `npm ERR! ERESOLVE unable to resolve dependency tree`
```bash
npm install --legacy-peer-deps
```

**Error**: `Cannot find module 'next-auth'`
```bash
npm install
```

### Can't log in

- Check both services are running
- Backend must be accessible at NEXT_PUBLIC_API_URL
- Check browser console for CORS errors

### Chat not responding

- Check backend is running on port 8000
- Look at backend terminal for errors
- Try a simpler message like "Add test"

### Database errors

The system creates tables automatically on first request. If you see database errors:
```bash
# Restart backend to trigger table creation
ctrl+c  # Stop backend
# Edit db.py if needed to force create_all()
uvicorn main:app --reload
```

---

## Architecture

```
Frontend (http://localhost:3000)
    ↓ JSON requests
    ↓ JWT auth
Backend (http://localhost:8000)
    ↓ Validates JWT
    ↓ Creates agent
    ↓ Calls MCP tools
    ↓ Queries database
Database (PostgreSQL)
    ↓ Stores users, tasks, conversations, messages
```

---

## Files to Know

### Backend
- `backend/main.py` - FastAPI app entry point
- `backend/models.py` - Database models (User, Task, Conversation, Message)
- `backend/mcp_server.py` - Task management tools
- `backend/agents.py` - AI agent with intent routing
- `backend/routes/chat.py` - Chat endpoint

### Frontend
- `frontend/app/page.tsx` - Login page
- `frontend/app/dashboard/page.tsx` - Task dashboard
- `frontend/app/chat/page.tsx` - Chat interface (NEW)
- `frontend/lib/api/chat-client.ts` - API communication (NEW)
- `frontend/components/chat/` - Chat UI components (NEW)

### Documentation
- `specs/5-ai-chatbot/spec.md` - User stories and requirements
- `specs/5-ai-chatbot/plan.md` - Technical architecture
- `specs/5-ai-chatbot/tasks.md` - 37-task breakdown
- `PHASE3_TESTING.md` - Testing guide
- `PHASE3_IMPLEMENTATION_SUMMARY.md` - Detailed overview

---

## Next Steps

1. ✅ Run the application locally
2. ✅ Test all user stories (PHASE3_TESTING.md)
3. ✅ Check the dashboard to see synced tasks
4. ✅ Try error cases (empty message, very long message)
5. ✅ Review the code (well-documented throughout)
6. Deploy to production (PHASE3_TESTING.md → Deployment section)

---

## Support

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **API Redoc**: http://localhost:8000/redoc (ReDoc)
- **Type Definitions**: Check `backend/schemas.py` and `frontend/lib/api/chat-client.ts`

---

**Happy chatting! 🚀**
