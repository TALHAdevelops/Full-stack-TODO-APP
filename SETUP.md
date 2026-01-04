# TaskFlow Complete Setup Guide

## Overview

TaskFlow is a full-stack task management application with:

- **Frontend**: Next.js 15 with React 19, TypeScript
- **Backend**: FastAPI with SQLModel ORM
- **Database**: PostgreSQL (Neon)
- **Authentication**: JWT with Better Auth

## Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn
- PostgreSQL database (Neon recommended)

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `backend/.env` file from `.env.example`:

```env
# Database URL (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# JWT Secret (minimum 32 characters)
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000
```

### 4. Run the Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will:

- Create database tables automatically on startup
- Be available at `http://localhost:8000`
- API docs at `http://localhost:8000/docs`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Create `frontend/.env.local` file from `.env.example`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Frontend URL
NEXT_PUBLIC_APP_URL=http://localhost:3000

# JWT Secret (must match backend!)
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long
```

### 3. Run the Frontend

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication

#### Register User

```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name"
}

Response:
{
  "access_token": "token",
  "token_type": "bearer",
  "user": {
    "id": "user-xxx",
    "email": "user@example.com",
    "name": "User Name",
    "created_at": "2024-01-04T..."
  }
}
```

#### Login User

```bash
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123

Response:
{
  "access_token": "token",
  "token_type": "bearer",
  "user": { ... }
}
```

#### Get Current User

```bash
GET /auth/me
Authorization: Bearer {token}

Response:
{
  "id": "user-xxx",
  "email": "user@example.com",
  "name": "User Name",
  "created_at": "2024-01-04T..."
}
```

### Tasks

All task endpoints require `Authorization: Bearer {token}` header

#### List Tasks

```bash
GET /api/tasks
```

#### Create Task

```bash
POST /api/tasks
Content-Type: application/json

{
  "title": "Task Title",
  "description": "Task description"
}
```

#### Get Task

```bash
GET /api/tasks/{task_id}
```

#### Update Task

```bash
PUT /api/tasks/{task_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description"
}
```

#### Toggle Task Status

```bash
PATCH /api/tasks/{task_id}/complete
```

#### Delete Task

```bash
DELETE /api/tasks/{task_id}
```

## Authentication Flow

### 1. User Registers

- Frontend POST to `/auth/register` with email, password, name
- Backend creates user with hashed password
- Backend returns JWT token
- Frontend stores token in localStorage

### 2. User Logs In

- Frontend POST to `/auth/token` with email and password
- Backend verifies credentials
- Backend returns JWT token
- Frontend stores token in localStorage

### 3. Authenticated Requests

- All API requests include `Authorization: Bearer {token}` header
- Backend validates token using JWT verification
- If token invalid or expired, returns 401 Unauthorized
- Frontend removes token and redirects to login

### 4. Dashboard Access

- On page load, checks for token in localStorage
- If no token, redirects to login page
- If token exists, fetches user data from `/auth/me`
- If 401 response, clears token and redirects to login
- Loads tasks from `/api/tasks`

## Database Schema

### Users Table

```sql
CREATE TABLE users (
  id VARCHAR PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR,
  password_hash VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
)
```

### Tasks Table

```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR NOT NULL REFERENCES users(id),
  title VARCHAR NOT NULL,
  description VARCHAR,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
```

## Frontend Pages

### `/` (Login Page)

- Sign In form for existing users
- Links to signup page

### `/signup` (Registration Page)

- Sign up form for new users
- Creates account and auto-logs in
- Redirects to dashboard on success

### `/dashboard` (Task Management)

- Requires authentication
- Displays user's tasks
- Create, edit, delete, and toggle task completion
- Real-time task updates

## Key Fixes Made

1. **Auth Routes**: Added `/auth/register` and `/auth/me` endpoints
2. **Token Management**: Proper JWT generation and validation
3. **CORS**: Configured to allow frontend-backend communication
4. **API Integration**: Frontend correctly calls backend endpoints
5. **Authentication Flow**: Proper token storage and validation on all requests
6. **Error Handling**: 401 Unauthorized redirects to login
7. **Database**: Proper schema with users and tasks tables

## Troubleshooting

### CORS Errors

- Ensure `FRONTEND_URL` in backend `.env` matches frontend origin
- Frontend should be at the URL specified in `.env`

### 401 Unauthorized

- Token may be expired (30-minute expiration)
- Token may be invalid or malformed
- Check localStorage has `auth_token`
- Clear localStorage and re-login

### Database Connection Error

- Verify `DATABASE_URL` is correct
- Check PostgreSQL is running
- Ensure network access to database

### API Not Responding

- Verify backend is running on `http://localhost:8000`
- Check `NEXT_PUBLIC_API_URL` matches backend URL
- Check CORS middleware is configured correctly

## Running in Production

### Backend

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend

```bash
npm run build
npm run start
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Better Auth Documentation](https://www.better-auth.com/)
