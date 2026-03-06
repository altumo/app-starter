# __PROJECT_NAME__

Full-stack application built with Django + React + PostgreSQL + Clerk + Docker.

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | React (Vite) + TypeScript + Tailwind CSS |
| Authentication | Clerk |
| Backend API | Django 5.2 LTS + Django REST Framework |
| Database | PostgreSQL 17 |
| Containers | Docker + Docker Compose |

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (includes Docker Compose)
- [Clerk account](https://dashboard.clerk.com/) (free tier available)

### 1. Get Clerk API Keys

1. Go to [dashboard.clerk.com](https://dashboard.clerk.com/)
2. Create an application (or use an existing one)
3. Go to **API Keys** and copy:
   - `Publishable key` (starts with `pk_test_`)
   - `Secret key` (starts with `sk_test_`)
4. Go to **API Keys > Advanced** and note your **JWKS URL**:
   `https://<your-instance>.clerk.accounts.dev/.well-known/jwks.json`

### 2. Configure Environment

```bash
# Copy environment files (auto-generated on first run, or do it manually)
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
```

Edit `.env`:
```bash
SECRET_KEY=<generate-a-random-key>
CLERK_SECRET_KEY=sk_test_your_key_here
CLERK_JWKS_URL=https://your-instance.clerk.accounts.dev/.well-known/jwks.json
```

Edit `frontend/.env.local`:
```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
```

### 3. Start Development

```bash
./start-local-dev.sh
```

That's it. The script handles everything:
- Starts PostgreSQL in Docker
- Runs Django migrations
- Installs npm dependencies
- Starts both servers with hot-reload

### Access Points

| Service | URL |
|---------|-----|
| Frontend | [http://localhost:3000](http://localhost:3000) |
| Backend API | [http://localhost:8000/api/](http://localhost:8000/api/) |
| Health Check | [http://localhost:8000/api/health/](http://localhost:8000/api/health/) |
| Django Admin | [http://localhost:8000/admin/](http://localhost:8000/admin/) |

## Project Structure

```
.
├── backend/                    # Django API
│   ├── apps/
│   │   ├── accounts/           # User model + Clerk JWT auth
│   │   └── core/               # Health check + utilities
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py         # Shared settings
│   │   │   ├── development.py  # Local dev settings
│   │   │   └── production.py   # Production settings
│   │   └── urls.py
│   ├── Dockerfile              # Production image
│   ├── entrypoint.sh           # Startup script (migrations + gunicorn)
│   └── requirements.txt
├── frontend/                   # React (Vite) app
│   ├── src/
│   │   ├── App.tsx             # Router + Clerk provider
│   │   ├── pages/              # Page components
│   │   ├── layouts/            # Layout components
│   │   ├── components/         # Shared components
│   │   └── lib/api.ts          # API client
│   ├── Dockerfile              # Production image (nginx)
│   ├── nginx.conf              # Production proxy + static serving
│   └── vite.config.ts          # Dev proxy config
├── docker-compose.yml          # Local development
├── docker-compose.prod.yml     # Production reference
├── .env.example                # Environment template
└── start-local-dev.sh          # One-command setup
```

## Development

### Running Commands

```bash
# Django management commands
docker compose exec backend python manage.py <command>

# Create a superuser
docker compose exec backend python manage.py createsuperuser

# Make migrations
docker compose exec backend python manage.py makemigrations

# Run migrations
docker compose exec backend python manage.py migrate

# npm commands
docker compose exec frontend npm <command>
```

### API Architecture

- Vite dev server proxies `/api/*` requests to Django via `vite.config.ts`
- In production, nginx proxies `/api/*` to Django and serves the static frontend bundle
- No CORS issues during development
- Clerk JWT tokens are passed as `Authorization: Bearer <token>` headers
- Django verifies tokens using Clerk's JWKS endpoint

### Authentication Flow

1. User signs in via Clerk (frontend)
2. Frontend gets session JWT from Clerk via `getToken()`
3. Frontend sends JWT as Bearer token to `/api/*` endpoints
4. Django's `ClerkJWTAuthentication` class verifies the JWT using JWKS
5. Request proceeds with authenticated `ClerkUser` object

## Production

### Build Production Images

```bash
docker compose -f docker-compose.prod.yml build
```

### Deploy

The production setup:
- Django runs behind Gunicorn with worker auto-scaling
- Frontend is served as static files by nginx, which also proxies `/api/*` to Django
- Entrypoint script waits for DB and runs migrations with advisory lock
- Both services include Docker health checks
- Static files served by WhiteNoise

### Environment Variables (Production)

In addition to development variables, set:
```bash
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

Ensure Clerk keys use `pk_live_` / `sk_live_` prefixes for production.
