# TaskFlow - Phase 2 (Full-Stack Todo Web App)

A production-ready, multi-user task management application built for search-driven development hackathons.

## Tech Stack
- **Frontend**: Next.js 15 (App Router), TypeScript, Tailwind CSS, better-auth
- **Backend**: FastAPI (Python 3.13), SQLModel (ORM), PyJWT
- **Database**: Neon Serverless PostgreSQL

## Features
- Full User Authentication (Sign Up, Sign In, Sign Out)
- Strict User Isolation (Each user sees ONLY their data)
- Full CRUD operations for Tasks (Create, Read, Update, Delete)
- Completion status toggle with optimistic UI updates
- Mobile-first responsive design
- Persistent storage in PostgreSQL

## Setup & Running

### Backend
1. `cd backend`
2. `python -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. Create `.env` based on `.env.example`
5. `uvicorn main:app --reload`

### Frontend
1. `cd frontend`
2. `npm install`
3. Create `.env.local` based on `.env.example`
4. `npm run dev`

## Deployment
- Frontend: Vercel
- Backend: Optional (RailWay / Render)
- Database: Neon.tech
