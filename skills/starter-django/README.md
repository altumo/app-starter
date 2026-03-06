# starter-django

Scaffolds a production-ready full-stack project with **Django + React + Vite + PostgreSQL + Clerk + Docker**.

## What You Get

```
myapp/
├── backend/                   # Django 5.2 + DRF + Gunicorn
│   ├── apps/
│   │   ├── accounts/          # Custom User model, Clerk JWT auth
│   │   └── core/              # Health check endpoint
│   ├── config/
│   │   └── settings/          # Split settings (base/dev/prod)
│   ├── Dockerfile             # Multi-stage production build
│   └── entrypoint.sh          # DB wait + advisory lock migrations
├── frontend/                  # React 19 + Vite + TypeScript
│   ├── src/
│   │   ├── pages/             # Home, SignIn, SignUp, Dashboard
│   │   ├── components/        # ProtectedRoute
│   │   ├── layouts/           # DashboardLayout with UserButton
│   │   └── lib/               # API fetch helpers (auth + unauth)
│   ├── Dockerfile             # Multi-stage nginx build
│   └── nginx.conf             # Reverse proxy for /api + SPA fallback
├── docker-compose.yml         # Dev: PostgreSQL + Django + Vite
├── docker-compose.prod.yml    # Prod: all services with restart policies
├── start-local-dev.sh         # One-command setup
└── .env.example               # All configuration documented
```

~45 files. Zero manual setup beyond Clerk keys.

## Install

```bash
npx skills add altumo/app-starter -s starter-django
```

## Usage

```bash
claude
```

```
bootstrap a new project called myapp
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Clerk account](https://dashboard.clerk.com) (free tier)

## Setup

### 1. Get Clerk keys

From [dashboard.clerk.com](https://dashboard.clerk.com):
- **Publishable key** (`pk_test_...`)
- **Secret key** (`sk_test_...`)
- **JWKS URL**: `https://<your-instance>.clerk.accounts.dev/.well-known/jwks.json`

### 2. Configure environment

Edit `.env`:
```bash
CLERK_JWKS_URL=https://your-instance.clerk.accounts.dev/.well-known/jwks.json
```

Edit `frontend/.env.local`:
```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_key
```

### 3. Start

```bash
./start-local-dev.sh
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/ |
| Health check | http://localhost:8000/api/health/ |
| Django Admin | http://localhost:8000/admin/ |

## Common Tasks

```bash
# Django management commands
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate

# Install packages
docker compose exec frontend npm install <package>
# Or add to backend/requirements.txt and rebuild:
docker compose up --build backend

# Logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop / reset
docker compose down        # stop
docker compose down -v     # stop + wipe database
```

## Architecture

- **Auth**: PyJWT + JWKS for Clerk JWT verification (zero dependency on Clerk's Python SDK)
- **Settings**: Split into `base.py`, `development.py`, `production.py` (no `if DEBUG` conditionals)
- **Dev proxy**: Vite proxies `/api/*` to Django (no CORS in development)
- **Prod proxy**: nginx serves the React build and proxies `/api/*` to Gunicorn
- **Migrations**: `pg_advisory_lock` prevents race conditions with multiple replicas
- **User model**: Custom `User` model from day one (Django best practice)

See [references/architecture.md](references/architecture.md) for detailed rationale.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Database not available" | Docker Desktop might still be starting. Wait and retry. |
| Clerk sign-in error | Check `VITE_CLERK_PUBLISHABLE_KEY` in `frontend/.env.local`. Restart: `docker compose restart frontend` |
| 401 on authenticated requests | Check `CLERK_JWKS_URL` in `.env`. Restart: `docker compose restart backend` |
| Port conflict | Change ports in `.env`: `BACKEND_PORT=8001`, `FRONTEND_PORT=3001`, `DB_PORT=5433` |
