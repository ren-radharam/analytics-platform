# Analytics Platform
A real-time analytics & reporting platform built with FastAPI + Next.js.
## Architecture
```
frontend/ # Next.js 14 (App Router) + TypeScript + Tailwind
backend/
app/
api/v1/ # FastAPI routers
services/ # Business logic
repositories/ # DB queries
models/ # SQLAlchemy ORM
schemas/ # Pydantic v2 models
workers/ # Celery tasks
core/ # Config, security, deps
```
## Features
- JWT auth with refresh tokens + role-based access (Owner/Admin/Analyst/Viewer)
- Multi-tenant org isolation at query layer
- Event ingestion API (single + batch) with API key auth
- CSV upload → async processing via Celery + Redis
- Custom dashboards with chart widgets (line, bar, pie, KPI)
- PostgreSQL with async SQLAlchemy 2.0 + Alembic migrations
- Structured logging, health check endpoint
## Tech Stack
- **Backend**: FastAPI, SQLAlchemy 2.0 async, Pydantic v2, Celery, Redis, PostgreSQL
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts, Zustand
## Quick Start
### Prerequisites
- Docker, Python 3.11+, Node.js 18+
### Backend
```bash
docker-compose up -d # Start PostgreSQL + Redis
cd backend && python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # Edit values
alembic upgrade head
uvicorn app.main:app --reload --port 8000
celery -A app.workers.celery_app worker --loglevel=info
```
### Frontend
```bash
cd frontend && npm install
cp .env.local.example .env.local
npm run dev
```
Open http://localhost:3000
## API Docs
Swagger UI: http://localhost:8000/docs
## Live Demo
- Frontend: https://your-app.vercel.app
- Backend: https://your-api.railway.app