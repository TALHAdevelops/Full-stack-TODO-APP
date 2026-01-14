# TaskFlow Phase III - Required Setup

**IMPORTANT**: Read this before running the application. Some manual configuration is required.

---

## ❌ What Will NOT Work Without Setup

1. **Agent responses** - Needs OpenAI API key
2. **Database persistence** - Needs PostgreSQL database
3. **Authentication** - Needs auth secrets configured

---

## ✅ Required Setup Steps

### Step 1: Get OpenAI API Key (5 minutes)

The agent uses OpenAI's GPT-4o model to understand natural language.

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy the key

### Step 2: Setup Backend Environment

Create `backend/.env`:

```env
# Database connection (REQUIRED)
DATABASE_URL=postgresql://username:password@localhost:5432/taskflow

# OR for Neon Cloud (recommended):
DATABASE_URL=postgresql://user:password@ep-xxxx.neon.tech/neondb?sslmode=require

# OpenAI API (REQUIRED for chat to work)
OPENAI_API_KEY=sk-your-api-key-here

# Authentication secrets (REQUIRED)
BETTER_AUTH_SECRET=generate-random-string-here-min-32-chars
NEXTAUTH_SECRET=generate-another-random-string-min-32-chars
```

**How to generate random secrets**:
```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows PowerShell:
[System.Convert]::ToBase64String((1..32 | ForEach-Object {Get-Random -Maximum 256})) | cut -c 1-32
```

### Step 3: Setup Frontend Environment

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=same-value-as-backend
NEXTAUTH_URL=http://localhost:3000
```

### Step 4: Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Step 5: Create Database (Choose One Option)

**Option A: Local PostgreSQL (if installed)**
```bash
# Create database
createdb taskflow

# Update backend/.env:
DATABASE_URL=postgresql://username:password@localhost:5432/taskflow
```

**Option B: Neon Cloud (Recommended - Free tier available)**
1. Go to https://console.neon.tech
2. Create account and project
3. Get connection string
4. Add to backend/.env:
   ```
   DATABASE_URL=postgresql://user:password@ep-xxxx.neon.tech/neondb?sslmode=require
   ```

### Step 6: Run the Application

**Terminal 1 - Backend**:
```bash
cd backend
uvicorn main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

Expected output:
```
▲ Next.js ready on http://localhost:3000
```

### Step 7: Test It Works

1. Open http://localhost:3000
2. Sign up with any email/password
3. Go to /chat
4. Send message: "Add test task"
5. Agent should respond with task confirmation

---

## 🔍 Troubleshooting

### "OPENAI_API_KEY not set" Warning

**Problem**: Agent won't respond or returns fallback messages

**Solution**:
1. Verify `backend/.env` has `OPENAI_API_KEY`
2. Restart backend: `ctrl+c` then `uvicorn main:app --reload`
3. Check backend terminal: should see "OpenAI client initialized"

### "Connection to postgres failed"

**Problem**: Database connection error

**Solution**:
1. Verify PostgreSQL is running (local) or accessible (Neon)
2. Check DATABASE_URL in `backend/.env`
3. Test connection:
   ```bash
   psql "your-database-url-here"
   ```

### "Module openai not found"

**Problem**: ImportError for openai

**Solution**:
```bash
cd backend
pip install openai
# OR re-install requirements:
pip install -r requirements.txt
```

### "Authentication failed" on Login

**Problem**: Can't log in

**Solution**:
1. Verify `BETTER_AUTH_SECRET` and `NEXTAUTH_SECRET` are set
2. Make sure both frontend and backend .env files have the same secrets
3. Restart both services

### "Cannot find module 'next-auth'"

**Problem**: Frontend npm install failed

**Solution**:
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

---

## 📊 Checklist Before Running

```
Backend Setup:
☐ pip install -r requirements.txt
☐ Created backend/.env
☐ Added DATABASE_URL
☐ Added OPENAI_API_KEY
☐ Added BETTER_AUTH_SECRET
☐ Database created and accessible
☐ Backend starts: uvicorn main:app --reload

Frontend Setup:
☐ npm install
☐ Created frontend/.env.local
☐ Added NEXT_PUBLIC_API_URL
☐ Added NEXTAUTH_SECRET
☐ Frontend starts: npm run dev

Testing:
☐ http://localhost:3000 loads (login page)
☐ Can create account
☐ Can navigate to /chat
☐ Can send message "Add test task"
☐ Agent responds with confirmation
```

---

## 💰 Cost Considerations

### OpenAI API Pricing
- ~$0.001-0.002 per message (with gpt-4o)
- Free tier: $5 credit for 3 months
- Recommended: Set usage limits in OpenAI dashboard

### Database Costs
- **Neon (Recommended)**: Free tier (no cost)
- **PostgreSQL Local**: Free
- **AWS RDS**: ~$9-15/month
- **Railway**: ~$5-10/month

---

## 🔒 Security Notes

1. **Never commit `.env` files** to git (already in .gitignore)
2. **Rotate API keys** if exposed
3. **Use strong secrets** for BETTER_AUTH_SECRET
4. **Keep database credentials safe**
5. **Use HTTPS in production** (HTTP only for local dev)

---

## 📖 Common Questions

**Q: Do I need OpenAI Pro?**
A: No, API key works with free or paid plan. Just need credit.

**Q: Can I use a different LLM?**
A: The code is built for OpenAI. To use Claude/Anthropic/others, you'd need to update `agents.py`.

**Q: What if I don't have a database?**
A: The app won't run. Use Neon (free) or install PostgreSQL locally.

**Q: Can I run without the OpenAI API key?**
A: Yes, but the agent will use fallback responses (just echoes user intent, doesn't actually run tools).

**Q: How do I reset my database?**
A: Drop and recreate:
```bash
dropdb taskflow
createdb taskflow
# Or in Neon: delete branch and create new one
```

---

## ✅ You're Ready When:

1. ✅ Backend .env configured with DATABASE_URL and OPENAI_API_KEY
2. ✅ Frontend .env.local configured with NEXT_PUBLIC_API_URL
3. ✅ Both dependencies installed (pip + npm)
4. ✅ Database created and accessible
5. ✅ Both services start without errors
6. ✅ Can log in and send a chat message

**Then proceed with QUICKSTART.md for full testing**

---

## Support

- **OpenAI Docs**: https://platform.openai.com/docs
- **Neon Docs**: https://neon.tech/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs

---

**All set? Start with QUICKSTART.md! 🚀**
