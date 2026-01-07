# 🎯 TaskFlow Web - Full-Stack Todo Application

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://talha-taskflow-web.vercel.app/)
[![Frontend](https://img.shields.io/badge/frontend-Next.js%2015-black)](https://nextjs.org/)
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/database-PostgreSQL-336791)](https://neon.tech/)

A production-ready, multi-user task management application with secure authentication and full CRUD capabilities. Built following **Spec-Driven Development (SDD)** principles.

## 🚀 Live Demo

- **Frontend**: [https://talha-taskflow-web.vercel.app/](https://talha-taskflow-web.vercel.app/)
- **Backend API**: [https://talha-taskflow-backend.vercel.app/](https://talha-taskflow-backend.vercel.app/)

## ✨ Features

### 🔐 Authentication & Security
- Secure user registration and login with JWT tokens
- Password hashing with bcrypt
- Better Auth integration for session management
- Strict user isolation - users can only access their own tasks

### ✅ Task Management
- **Create** new tasks with title and description
- **Read** all your tasks in a clean dashboard
- **Update** existing tasks with inline editing
- **Delete** tasks with confirmation modals
- **Toggle** completion status with optimistic UI updates

### 🎨 User Experience
- Modern, clean UI with Tailwind CSS
- Mobile-first responsive design
- Modal-based forms for better UX
- Real-time feedback and error handling
- Accessible components with proper ARIA labels

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Auth**: Better Auth
- **Icons**: Lucide React
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI (Python 3.13)
- **ORM**: SQLModel
- **Auth**: PyJWT + bcrypt
- **Database**: Neon Serverless PostgreSQL
- **Deployment**: Vercel

## 📁 Project Structure

```
TALHA-HTFA/
├── frontend/                 # Next.js frontend application
│   ├── app/                 # App router pages and layouts
│   ├── components/          # Reusable UI components
│   ├── lib/                 # API client, types, utilities
│   └── public/              # Static assets
├── backend/                 # FastAPI backend application
│   ├── routes/              # API route handlers
│   ├── models.py            # SQLModel database models
│   ├── schemas.py           # Pydantic validation schemas
│   ├── auth.py              # JWT middleware
│   ├── main.py              # FastAPI app entry point
│   └── vercel.json          # Vercel deployment config
└── specs/                   # SDD specification documents
    ├── sp.constitution      # Project principles
    ├── sp.specify           # Functional requirements
    ├── sp.plan              # Technical strategy
    └── sp.tasks             # Task breakdown
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.13+
- PostgreSQL database (or Neon account)

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```env
   DATABASE_URL=postgresql://user:password@host/database
   BETTER_AUTH_SECRET=your-secret-key
   FRONTEND_URL=http://localhost:3000
   ```

5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```
   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   BETTER_AUTH_SECRET=your-secret-key
   BETTER_AUTH_URL=http://localhost:3000
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```
   Frontend will be available at `http://localhost:3000`

## 🌐 Deployment

### Deploying to Vercel

#### Backend
1. Push your code to GitHub
2. Import project to Vercel
3. Set root directory to `backend`
4. Add environment variables:
   - `DATABASE_URL`
   - `BETTER_AUTH_SECRET`
   - `FRONTEND_URL`

#### Frontend
1. Import project to Vercel (separate project)
2. Set root directory to `frontend`
3. Add environment variables:
   - `NEXT_PUBLIC_API_URL` (your backend URL)
   - `NEXT_PUBLIC_APP_URL` (your frontend URL)
   - `BETTER_AUTH_SECRET`
   - `BETTER_AUTH_URL`

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/token` - Login and get JWT token
- `GET /auth/me` - Get current user info

#### Tasks
- `GET /api/tasks` - Get all tasks for current user
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle task completion

## 🏗️ Development Approach

This project follows **Spec-Driven Development (SDD)**:
1. ✅ **Constitution** - Core principles and security standards defined
2. ✅ **Specification** - Functional requirements documented
3. ✅ **Planning** - Technical implementation strategy created
4. ✅ **Tasks** - Itemized breakdown (T-201 to T-237)
5. ✅ **Implementation** - All phases completed
6. ✅ **Deployment** - Live on Vercel

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

**Talha**

- GitHub: [@TALHAdevelops](https://github.com/TALHAdevelops)
- Live Demo: [TaskFlow Web](https://talha-taskflow-web.vercel.app/)

## 🙏 Acknowledgments

- Built with guidance from Claude Code
- Deployed on Vercel
- Database hosted on Neon
- Following SDD principles for clean architecture
