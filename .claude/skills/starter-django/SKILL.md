---
name: starter-django
description: Bootstrap a production-ready full-stack project with Django + React + Vite + PostgreSQL + Clerk + Docker. Use when starting a new project or when the user says "bootstrap", "scaffold", "starter", "new project", or "init project". Creates turn-key local development with a single command.
---

# Starter Django: Full-Stack Project Bootstrap

## Overview

This skill creates a complete, production-ready full-stack project with:
- **Backend**: Django 5.2 LTS + Django REST Framework + Gunicorn
- **Frontend**: React (Vite) + TypeScript + Tailwind CSS
- **Auth**: Clerk (JWT verification in Django, Clerk provider in React)
- **Database**: PostgreSQL 17 with safe migration handling
- **Containers**: Docker Compose for local dev, production Dockerfiles

## When to Use

- "Bootstrap a new project"
- "Create a new Django + React project"
- "Scaffold a full-stack app"
- "Set up a new project with Clerk"
- "Init project" or "starter"
- Any request to create a new project using this stack

## Prerequisites

The host machine needs:
- Docker and Docker Compose
- Git

That's it. Everything else runs in containers.

## Instructions

Follow these steps exactly. Read template files from `assets/templates/` relative to this skill directory and write them to the project root. The skill directory is the directory containing this SKILL.md file.

### Step 1: Determine Project Configuration

Ask the user for (or use defaults):
- **Project name** (default: basename of current directory, e.g. `myproject`)
- **Django app name** (default: `api`)

Use the project name in Django settings module. Replace `__PROJECT_NAME__` in all templates.

### Step 2: Initialize Git Repository

```bash
# Only if not already a git repo
if [ ! -d .git ]; then
  git init
fi
```

### Step 3: Create the Backend

1. Read and write all files from `assets/templates/backend/` to `./backend/` in the project root
2. Replace `__PROJECT_NAME__` with the actual project name in all files
3. Create `backend/manage.py` with Django standard manage.py pointing to `config.settings.development`
4. Create `backend/apps/__init__.py`, `backend/apps/accounts/__init__.py`, `backend/apps/core/__init__.py`
5. Create `backend/config/__init__.py`, `backend/config/settings/__init__.py`

After writing all backend files, the structure should be:
```
backend/
├── manage.py
├── requirements.txt
├── Dockerfile
├── entrypoint.sh
├── gunicorn.conf.py
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    ├── __init__.py
    ├── accounts/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── admin.py
    │   ├── managers.py
    │   ├── authentication.py
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── apps.py
    │   └── migrations/
    │       └── __init__.py
    └── core/
        ├── __init__.py
        ├── views.py
        ├── urls.py
        └── apps.py
```

### Step 4: Create the Frontend

1. Read and write all files from `assets/templates/frontend/` to `./frontend/` in the project root
2. Create the Vite SPA directory structure:

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── SignIn.tsx
│   │   ├── SignUp.tsx
│   │   └── Dashboard.tsx
│   ├── layouts/
│   │   └── DashboardLayout.tsx
│   ├── components/
│   │   └── ProtectedRoute.tsx
│   └── lib/
│       └── api.ts
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
├── nginx.conf
├── Dockerfile
├── .env.local.example
└── .gitignore
```

3. The frontend `package.json` already includes `@clerk/clerk-react` as a dependency
4. Replace `__PROJECT_NAME__` with the actual project name in all files

### Step 5: Create Root Configuration Files

Write these files to the project root from templates:
- `docker-compose.yml`
- `docker-compose.prod.yml`
- `.env.example`
- `.gitignore`
- `start-local-dev.sh` (make executable with `chmod +x`)
- `README.md`

### Step 6: Generate .env File

Create `.env` from `.env.example` with local development defaults:
- Generate a random Django SECRET_KEY using: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- Set DATABASE_URL to point to the Docker Postgres
- Leave CLERK keys as placeholders (user must get from Clerk dashboard)

### Step 7: Verify Structure

Run `find . -type f | head -60` to verify the project structure looks correct.

### Step 8: Print Next Steps

Tell the user:

```
Project bootstrapped successfully!

Next steps:
1. Get your Clerk API keys from https://dashboard.clerk.com
2. Update .env with your CLERK_SECRET_KEY and CLERK_JWKS_URL
3. Update frontend/.env.local with your VITE_CLERK_PUBLISHABLE_KEY
4. Run: ./start-local-dev.sh

The app will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Health check: http://localhost:8000/api/health/
```

## Architecture Notes

Read `references/architecture.md` for detailed architecture decisions if needed.

## Important Details

- **Always create the custom User model first** - Django does not support changing AUTH_USER_MODEL after the first migration
- **Never hardcode secrets** - all sensitive values come from environment variables
- **The entrypoint.sh uses pg_advisory_lock** to prevent migration race conditions when multiple containers start simultaneously
- **Vite dev server proxies /api/* to Django** during development, eliminating CORS issues
- **Production uses nginx to proxy /api/* to Django** and serve the static frontend bundle
