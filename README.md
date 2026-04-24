# Review Agent

> Full-stack review analytics platform built with FastAPI + Celery + LangGraph + Chroma + Vue.
> 
> It turns raw product reviews into structured negative-feedback insights with async processing, retrieval-augmented analysis, and a complete login-based user flow.

---

## 1. Project Overview

Review Agent is an end-to-end project for product review analysis.

It is designed to solve a common product-ops problem: teams receive many reviews, but negative feedback is scattered and hard to action quickly.

This project provides:

- account-based access (register/login/refresh/logout/me)
- async report generation pipeline (queue + worker)
- structured analysis output (summary, reasons, keywords, suggestions)
- similar historical case retrieval with vector search
- front-end dashboard for task submission, polling, and visualization

---

## 2. Why This Project Matters

### Business pain points

1. Manual review triage is slow when data volume grows.
2. Negative feedback often lacks structured categorization.
3. Similar historical complaints are hard to reuse.
4. Token-copy testing flow does not match real product usage.

### What this project delivers

- login-first product flow instead of manual token input
- automated negative-review insight extraction
- reusable case recall via Chroma Top-K retrieval
- visual dashboard for decision-friendly report reading

---

## 3. Core Features

### 3.1 Auth Center (Backend)

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/forgot-password` (placeholder generic response)

### 3.2 Report APIs (Auth required)

- `POST /api/v1/reports/analyze` → submit job, return `task_id`
- `GET /api/v1/reports/status/{task_id}` → polling status
- `GET /api/v1/reports/{task_id}` → fetch final report

### 3.3 Frontend Dashboard (Vue)

- login/register switch panel
- authenticated report task submission
- auto polling task status
- report detail view with charts and similar cases

---

## 4. System Architecture

```text
[ Vue Dashboard ]
       |
       | HTTP (JWT access token)
       v
[ FastAPI API Layer ] ----------------------+
       |                                     |
       | enqueue task                        | read/write
       v                                     v
[ Celery + Redis Queue ]                [ PostgreSQL ]
       |
       | run async workflow
       v
[ LangGraph Analysis Pipeline ]
       |
       | retrieve similar reviews
       v
[ Chroma Vector Store ]
       |
       v
[ Structured Analysis Report ]
```

### Processing flow

1. User logs in and submits `product_id`.
2. API creates async task and returns `task_id`.
3. Worker loads reviews from DB.
4. Reviews are indexed/retrieved via Chroma.
5. LangGraph runs multi-node analysis.
6. Result is stored and exposed by report APIs.
7. Frontend polls until `completed` and renders charts/tables.

---

## 5. Tech Stack

### Backend

- FastAPI
- SQLAlchemy (async) + asyncpg
- Celery + Redis
- LangGraph
- ChromaDB
- JWT auth (access + refresh session model)

### Frontend

- Vue 3 + TypeScript + Vite
- Axios (access auto-inject + 401 refresh once)
- ECharts + vue-echarts

### Infra

- Docker Compose
- Services: `api`, `worker`, `frontend`, `postgres`, `redis`

---

## 6. Quick Start

### 6.1 Prepare env files

In project root `review-agent`:

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env
```

PowerShell alternative:

```powershell
copy .env.example .env
copy frontend\.env.example frontend\.env
```

### 6.2 Start all services

```bash
docker compose up -d --build
```

### 6.3 Open directly

- Backend Swagger: `http://localhost:8000/docs`
- Frontend Dashboard: `http://localhost:5173`
- Health check: `http://localhost:8000/health`

---

## 7. Default Login (for local demo)

Default admin account is initialized on startup:

- username: `admin`
- password: `Admin@123456`

You can override in `.env`:

- `DEFAULT_ADMIN_USERNAME`
- `DEFAULT_ADMIN_PASSWORD`
- `DEFAULT_ADMIN_EMAIL`

---

## 8. Frontend Usage Flow

1. Open `http://localhost:5173`
2. Login with admin (or register a new user)
3. Input `product_id` (optional date range)
4. Click `开始分析`
5. Wait until task status becomes `completed`
6. Read summary, categories, keywords, suggestions, trend chart, and similar cases

---

## 9. API Contract Snapshot

### 9.1 Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "Admin@123456"
}
```

### 9.2 Submit analyze task

```http
POST /api/v1/reports/analyze
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "product_id": "p001",
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-03-31"
  }
}
```

### 9.3 Response example

```json
{
  "task_id": "4f5d6f8e-..."
}
```

---

## 10. Testing

Run backend tests in container:

```bash
docker compose exec api bash -lc "pip install -r requirements.txt && python -m pytest --cov=app --cov-report=term-missing"
```

Run frontend build check:

```bash
docker compose exec frontend npm run build
```

---

## 11. Project Structure

```text
review-agent/
├─ app/
│  ├─ core/                 # config, LangGraph, RAG
│  ├─ crud/                 # DB data access
│  ├─ dependencies/         # auth/db/current_user deps
│  ├─ models/               # SQLAlchemy models
│  ├─ routers/              # auth + reports routes
│  ├─ schemas/              # request/response schemas
│  ├─ services/             # auth/report/task/bootstrap logic
│  └─ utils/                # unified exceptions
├─ frontend/
│  ├─ src/api/              # axios client + auth refresh logic
│  ├─ src/types/            # TS interfaces
│  └─ src/App.vue           # login + dashboard UI
├─ tests/                   # router/service/rag/agent tests
├─ docker-compose.yml
└─ requirements.txt
```

---

## 12. Resume-Oriented Highlights

This section can be reused directly in your resume bullets.

- Designed and implemented a full-stack review analytics platform with FastAPI, Celery, LangGraph, Chroma, and Vue.
- Built a production-style authentication center (register/login/refresh/logout/me) and migrated frontend from manual token input to login-first workflow.
- Implemented async task orchestration and status polling for long-running analysis jobs.
- Added vector retrieval of historical similar negative reviews to improve actionability of generated reports.
- Delivered end-to-end Docker Compose local environment with API docs, frontend dashboard, and test coverage workflow.

---

## 13. Security Notes

- Never commit real secrets to `.env.example`.
- Rotate any leaked key immediately.
- Use secret manager for production environments.
- Keep JWT secrets and DB credentials out of source control.

---

## 14. Roadmap

- Add Alembic migrations for users/auth_sessions/reviews
- Implement real password reset + email verification
- Add auth rate limiting and audit logs
- Add task metrics (latency/failure reason/queue depth)
- Split frontend into route-level pages (Login/Dashboard)

---

## 15. License

Internal project, follow your team policy for external publication.
