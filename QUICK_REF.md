# TaskFlow - Quick Reference

## Project Structure

```
TALHA-HTFA/
├── backend/              # FastAPI Python backend
│   ├── main.py          # App entry point with CORS
│   ├── db.py            # Database setup
│   ├── config.py        # Environment config
│   ├── models.py        # User & Task models
│   ├── schemas.py       # Request/response schemas
│   ├── auth.py          # JWT verification
│   ├── routes/          # API endpoints
│   │   ├── auth_routes.py   # Auth endpoints
│   │   ├── tasks.py         # Task endpoints
│   │   └── users.py         # User endpoints
│   ├── requirements.txt  # Dependencies
│   ├── .env.example     # Environment template
│   └── venv/            # Virtual environment
│
├── frontend/            # Next.js React frontend
│   ├── app/            # App router
│   │   ├── page.tsx            # Login page
│   │   ├── dashboard/page.tsx   # Task dashboard
│   │   ├── signup/page.tsx      # Registration
│   │   └── api/auth/            # Auth routes
│   ├── components/     # React components
│   │   ├── auth/       # Auth forms
│   │   ├── tasks/      # Task components
│   │   ├── ui/         # Reusable UI
│   │   └── layout/     # Layout
│   ├── lib/           # Utilities
│   │   ├── api.ts     # API calls
│   │   ├── types.ts   # TypeScript types
│   │   └── auth.ts    # Auth config
│   ├── package.json   # Dependencies
│   ├── .env.local     # Environment vars
│   └── .env.example   # Environment template
│
├── SETUP.md           # Complete setup guide
├── FIXES.md          # All fixes applied
└── README.md         # Project info

```

## Key Files Changed

### Backend

1. **routes/auth_routes.py** - Added `/auth/register` and `/auth/me` endpoints
2. **schemas.py** - Updated UserResponse with proper config
3. **config.py** - Environment setup
4. **main.py** - CORS configuration

### Frontend

1. **components/auth/SignUpForm.tsx** - Fixed to use `/auth/register`
2. **app/dashboard/page.tsx** - Fixed authentication check
3. **lib/api.ts** - Added `getCurrentUser()` function
4. **components/layout/Header.tsx** - Fixed logout
5. **components/tasks/DeleteConfirmDialog.tsx** - Updated styling

## API Endpoints

### Authentication

- `POST /auth/register` - Create account
- `POST /auth/token` - Login
- `GET /auth/me` - Get current user

### Tasks

- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task
- `PUT /api/tasks/{id}` - Update task
- `PATCH /api/tasks/{id}/complete` - Toggle completion
- `DELETE /api/tasks/{id}` - Delete task

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://...?sslmode=require
BETTER_AUTH_SECRET=min-32-characters
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
BETTER_AUTH_SECRET=min-32-characters (same as backend!)
```

## Token Management

**Storage**: localStorage with key `auth_token`

**Format**: JWT Bearer token in Authorization header

```
Authorization: Bearer {token}
```

**Expiration**: 30 minutes

**On Expiry**: 401 response triggers redirect to login

## Database Models

### User

```python
- id: str (primary key)
- email: str (unique)
- name: str
- password_hash: str
- created_at: datetime
```

### Task

```python
- id: int (primary key)
- user_id: str (foreign key → users.id)
- title: str
- description: str
- completed: bool
- created_at: datetime
- updated_at: datetime
```

## Common Commands

### Backend

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
uvicorn main:app --reload

# API Docs
http://localhost:8000/docs
```

### Frontend

```bash
# Setup
cd frontend
npm install

# Run dev
npm run dev

# Build
npm run build

# Start production
npm run start
```

## Debugging Tips

### 401 Unauthorized

- Check token in localStorage
- Verify BETTER_AUTH_SECRET matches backend
- Check Authorization header format
- Token may be expired

### CORS Errors

- Verify FRONTEND_URL in backend .env
- Check frontend origin matches
- Ensure CORS middleware is active

### API Not Found

- Check endpoint path spelling
- Verify backend is running on :8000
- Check NEXT_PUBLIC_API_URL is correct

### Database Connection Failed

- Verify DATABASE_URL is correct
- Check PostgreSQL is running
- Test connection string

## Testing Workflow

1. Register new account
2. Login with credentials
3. Create task
4. Edit task
5. Toggle completion
6. Delete task
7. Logout

All operations should complete without errors.

## Technology Stack

- **Language**: Python 3.9+, TypeScript 5.9
- **Backend**: FastAPI 0.109, SQLModel 0.0.14
- **Frontend**: Next.js 15, React 19
- **Database**: PostgreSQL
- **Auth**: JWT with Better Auth
- **Styling**: Tailwind CSS
- **Icons**: Lucide React

## Performance Notes

- JWT tokens: 30-minute expiration
- Database pooling: 5 connections
- API rate limiting: None (add if needed)
- CORS: Allow all headers/methods from frontend

## Production Checklist

- [ ] Set production DATABASE_URL
- [ ] Use strong BETTER_AUTH_SECRET (32+ characters)
- [ ] Set FRONTEND_URL to production domain
- [ ] Enable HTTPS
- [ ] Set NODE_ENV=production
- [ ] Configure rate limiting
- [ ] Setup database backups
- [ ] Monitor error logs
- [ ] Test end-to-end flows
- [ ] Setup SSL/TLS certificates

## Support

For detailed setup instructions, see [SETUP.md](./SETUP.md)
For all changes applied, see [FIXES.md](./FIXES.md)
