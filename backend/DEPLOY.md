# Vercel Deployment Guide

## Prerequisites

- Vercel account (free tier works)
- Neon PostgreSQL database (or compatible)
- Git repository pushed to GitHub/GitLab/Bitbucket

## Environment Variables

Set these in Vercel project settings (Settings > Environment Variables):

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string | `postgresql://...` |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (use a strong random string) | `your-secret-here` |
| `FRONTEND_URL` | No | Production frontend URL for CORS | `https://your-app.vercel.app` |

## Deployment Steps

### 1. Push Code to Git

```bash
git add .
git commit -m "Configure backend for Vercel deployment"
git push origin main
```

### 2. Import Project in Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New" > "Project"
3. Select your Git repository
4. Keep default settings (Framework Preset: Other, Root Directory: `./`)

### 3. Configure Environment Variables

In the Vercel dashboard for your project:

1. Go to Settings > Environment Variables
2. Add each required variable (see table above)
3. Select all environments (Production, Preview, Development)

### 4. Deploy

Click "Deploy" and Vercel will:
- Install dependencies from `backend/requirements.txt`
- Use Python 3.12 runtime
- Deploy your FastAPI app as a serverless function

## Testing

After deployment:

1. Visit your Vercel URL + `/health` to verify health: `https://your-app.vercel.app/health`
2. Test API endpoints: `https://your-app.vercel.app/`

## Troubleshooting

### 500 Internal Server Error

- Check Vercel Function Logs in the dashboard
- Verify all environment variables are set
- Ensure `DATABASE_URL` includes `sslmode=require`

### Database Connection Issues

- Neon URLs should include `?sslmode=require`
- Verify database is not paused (Neon auto-pauses)

### CORS Errors

- Ensure `FRONTEND_URL` matches your deployed frontend domain
- You can set multiple origins with commas: `http://localhost:3000,https://app.vercel.app`

## Local Development

Run locally with:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

API will be at `http://localhost:8000`
