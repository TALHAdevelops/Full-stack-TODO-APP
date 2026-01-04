# TaskFlow - Troubleshooting Guide

## Common Issues & Solutions

### 1. Backend Server Won't Start

#### Error: `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

#### Error: Database connection error

```
psycopg2.OperationalError: connection failed
```

**Cause**: DATABASE_URL is incorrect or database is unreachable

**Solution:**

1. Verify DATABASE_URL in `backend/.env`
2. Check PostgreSQL is running
3. Test connection:

```bash
psql your_database_url
```

#### Error: Port 8000 already in use

```
Address already in use
```

**Solution:**

```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>

# Or use different port:
uvicorn main:app --reload --port 8001
```

### 2. Frontend Issues

#### Blank page or "Cannot find module"

**Cause**: Missing dependencies

**Solution:**

```bash
cd frontend
npm install
npm run dev
```

#### Environment variables not loading

**Cause**: Wrong variable names or file location

**Solution:**

1. Ensure file is named `.env.local` (not `.env`)
2. Variables must start with `NEXT_PUBLIC_`
3. Restart dev server after changing `.env.local`
4. Check in browser DevTools:

```javascript
console.log(process.env.NEXT_PUBLIC_API_URL);
```

#### Port 3000 already in use

**Solution:**

```bash
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :3000
kill -9 <PID>

# Or use different port:
npm run dev -- -p 3001
```

### 3. Authentication Issues

#### "401 Unauthorized" on API calls

**Possible Causes:**

1. Token not stored in localStorage
2. Authorization header not sent
3. Token is expired (30 min expiration)
4. BETTER_AUTH_SECRET mismatch

**Solution:**

```javascript
// Check localStorage:
console.log(localStorage.getItem("auth_token"));

// Check headers in Network tab (DevTools)
// Should see: Authorization: Bearer <token>

// Clear and re-login:
localStorage.removeItem("auth_token");
// Refresh page, login again
```

#### Can't login - "Incorrect email or password"

**Check:**

1. Email/password are correct
2. Account was created successfully
3. Check database has user:

```sql
SELECT * FROM users WHERE email = 'your@email.com';
```

#### Signup page redirects to login instead of dashboard

**Cause**: Token not being stored or used correctly

**Solution:**

1. Check localStorage after signup:

```javascript
console.log(localStorage.getItem("auth_token"));
```

2. Check browser console for errors
3. Verify API response includes access_token:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123","name":"Test"}'
```

### 4. CORS Issues

#### "No 'Access-Control-Allow-Origin' header"

**Cause**: FRONTEND_URL doesn't match request origin

**Solution:**

1. Check `backend/.env`:

```env
FRONTEND_URL=http://localhost:3000
```

2. Frontend must be running at exact same origin
3. If using different port, update FRONTEND_URL:

```env
FRONTEND_URL=http://localhost:3001
```

4. Restart backend after changing

#### Browser blocks request with CORS error

**Check:**

1. Backend CORS middleware is active (it is in main.py)
2. Request includes proper headers (handled by api.ts)
3. Backend is accessible from frontend origin

**Debug:**

```bash
# Test from backend:
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     http://localhost:8000/auth/register
```

### 5. Database Issues

#### "Email already registered" when creating new account

**Expected behavior** - Email must be unique

**Solution:**

1. Use different email
2. Or clear database and start fresh:

```sql
DELETE FROM tasks;
DELETE FROM users;
```

#### Data not persisting after server restart

**Cause**: Database not connected or tables not created

**Check:**

1. Verify DATABASE_URL
2. Check tables exist:

```sql
\dt
```

3. Backend startup log should show "Create database tables"

#### Slow database queries

**Solution:**

1. Add indexes (done in schema)
2. Limit results in queries
3. Use connection pooling (enabled in db.py)

### 6. Token & Session Issues

#### Logged in but dashboard shows empty/redirect to login

**Cause**: Token verification failing

**Check:**

1. BETTER_AUTH_SECRET must match between backend and frontend
2. Token hasn't expired (30 min)
3. Check network tab for 401 responses

**Verify Secret:**

```bash
# Backend .env
echo $BETTER_AUTH_SECRET

# Frontend .env.local
echo $BETTER_AUTH_SECRET
```

They must be **identical**!

#### "Invalid token" error on dashboard

**Solution:**

```javascript
// Clear bad token:
localStorage.removeItem("auth_token");
// Login again
```

### 7. Task Operations Issues

#### Can't create/edit/delete tasks - 401 error

**Cause**: Token not being sent with request

**Check:**

1. Token in localStorage: `localStorage.getItem('auth_token')`
2. Authorization header in request (check DevTools Network tab)
3. Token format: `Bearer {token}`

#### Task list shows old data after creating new task

**Solution:**

1. Page refresh might be needed
2. Check browser console for errors
3. Verify task was created in database

### 8. TypeScript/Build Errors

#### "Cannot find type definitions"

**Solution:**

```bash
cd frontend
npm install
# Clear cache:
rm -rf .next node_modules
npm install
```

#### "Property 'auth_token' does not exist"

**Cause**: localStorage type mismatch

**Fix**: Use type assertion:

```typescript
const token = localStorage.getItem("auth_token") as string | null;
```

### 9. Production Deployment Issues

#### Backend won't start in production

```bash
# Use production server:
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

#### Frontend build fails

```bash
# Check build:
npm run build

# If fails, try:
rm -rf .next
npm install
npm run build
```

#### Environment variables not set in production

**Solution:**

1. Set env vars in hosting platform
2. Restart application
3. Never commit .env files

### 10. Network/Connectivity Issues

#### "Failed to fetch" errors

**Possible causes:**

1. Backend not running
2. Wrong API URL (check NEXT_PUBLIC_API_URL)
3. Network firewall blocking requests

**Check:**

```javascript
// Test API connectivity:
fetch("http://localhost:8000/health")
  .then((r) => r.json())
  .then(console.log);
```

#### Slow API responses

**Solutions:**

1. Check database query performance
2. Add caching headers
3. Optimize database queries
4. Check network latency

## Debug Mode

### Enable detailed logging

**Backend** - Change in `db.py`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Enable SQL logging
)
```

**Frontend** - Add to components:

```javascript
console.log("Debug:", {
  token: localStorage.getItem("auth_token"),
  apiUrl: process.env.NEXT_PUBLIC_API_URL,
  timestamp: new Date(),
});
```

## Testing Checklist

Run through this to verify everything works:

- [ ] Backend starts without errors
- [ ] Frontend builds without errors
- [ ] Can access http://localhost:3000
- [ ] Signup page loads
- [ ] Can create account with valid email/password
- [ ] Auto-redirects to dashboard after signup
- [ ] Dashboard loads with user info
- [ ] Can create task
- [ ] Task appears in list
- [ ] Can edit task
- [ ] Can toggle task completion
- [ ] Can delete task with confirmation
- [ ] Logout button works
- [ ] After logout, redirect to login
- [ ] Can login with existing credentials
- [ ] All API calls show 200/201 status codes
- [ ] No 401 errors when authenticated
- [ ] No CORS errors in console

## Getting Help

If still stuck:

1. **Check logs**: Look at backend/frontend console output
2. **Check browser DevTools**: Network tab, Console tab
3. **Verify environment**: Echo all env variables
4. **Database check**: Connect and query directly
5. **Test endpoints**: Use curl or Postman
6. **Clear everything**: Delete node_modules, venv, .env files
7. **Start fresh**: Follow SETUP.md from scratch

## Contact

Review:

- [SETUP.md](./SETUP.md) - Complete setup guide
- [FIXES.md](./FIXES.md) - What was fixed
- [QUICK_REF.md](./QUICK_REF.md) - Quick reference
