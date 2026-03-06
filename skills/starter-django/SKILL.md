---
name: starter-django
description: Bootstrap a production-ready Django project with Django + PostgreSQL + Tailwind CSS + Docker. Use when starting a new project or when the user says "bootstrap", "scaffold", "starter", "new project", or "init project". Creates turn-key local development with a single command.
---

# Starter Django: Project Bootstrap

## Overview

This skill creates a complete, production-ready Django project with:
- **Backend**: Django 5.2 LTS + Gunicorn
- **Auth**: django-allauth (email/password, social login ready)
- **Styling**: Tailwind CSS v4 (standalone CLI, no Node.js)
- **Database**: PostgreSQL 17 with safe migration handling
- **Containers**: Docker Compose for local dev, multi-stage production Dockerfile

## When to Use

- "Bootstrap a new project"
- "Create a new Django project"
- "Scaffold a web app"
- "Set up a new project"
- "Init project" or "starter"
- Any request to create a new project using this stack

## Prerequisites

The host machine needs:
- Docker and Docker Compose
- Git

That's it. Everything else runs in containers. No Node.js required.

## Instructions

Follow these steps exactly. Read template files from `assets/templates/` relative to this skill directory and write them to the project root. The skill directory is the directory containing this SKILL.md file.

### Step 1: Determine Project Configuration

Ask the user for (or use defaults):
- **Project name** (default: basename of current directory, e.g. `myproject`)

Use the project name in Django settings module. Replace `__PROJECT_NAME__` in all templates.

### Step 2: Initialize Git Repository

```bash
# Only if not already a git repo
if [ ! -d .git ]; then
  git init
fi
```

### Step 3: Create the Django Project

1. Read and write all files from `assets/templates/` to the project root
2. Replace `__PROJECT_NAME__` with the actual project name in all files
3. Create these empty `__init__.py` files:
   - `apps/__init__.py`
   - `apps/accounts/__init__.py`
   - `apps/accounts/migrations/__init__.py`
   - `apps/core/__init__.py`
   - `apps/pages/__init__.py`
   - `config/__init__.py`
   - `config/settings/__init__.py`

After writing all files, the structure should be:
```
manage.py
requirements.txt
Dockerfile
entrypoint.sh
gunicorn.conf.py
docker-compose.yml
.env.example
.gitignore
start-local-dev.sh
README.md
config/
├── __init__.py
├── settings/
│   ├── __init__.py
│   ├── base.py
│   ├── development.py
│   └── production.py
├── urls.py
├── wsgi.py
└── asgi.py
apps/
├── __init__.py
├── accounts/
│   ├── __init__.py
│   ├── models.py
│   ├── admin.py
│   ├── managers.py
│   ├── apps.py
│   └── migrations/
│       └── __init__.py
├── core/
│   ├── __init__.py
│   ├── views.py
│   └── apps.py
└── pages/
    ├── __init__.py
    ├── views.py
    └── apps.py
templates/
├── base.html
├── pages/
│   ├── home.html
│   └── dashboard.html
└── allauth/
    ├── layouts/
    │   └── base.html
    └── elements/
        ├── button.html
        ├── field.html
        ├── form.html
        ├── h1.html
        ├── h2.html
        ├── hr.html
        ├── alert.html
        ├── panel.html
        └── p.html
static/
└── css/
    └── input.css
```

### Step 4: Generate .env File

Create `.env` from `.env.example` with local development defaults:
- Generate a random Django SECRET_KEY using: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- Set DATABASE_URL to point to the Docker Postgres

### Step 5: Make Scripts Executable

```bash
chmod +x start-local-dev.sh
```

### Step 6: Verify Structure

Run `find . -type f | head -60` to verify the project structure looks correct.

### Step 7: Print Next Steps

Tell the user:

```
Project bootstrapped successfully!

Next steps:
1. Run: ./start-local-dev.sh
2. Open http://localhost:8000

The app will be available at:
- Home page: http://localhost:8000
- Sign up: http://localhost:8000/accounts/signup/
- Dashboard: http://localhost:8000/dashboard/ (requires login)
- Health check: http://localhost:8000/health/
- Django Admin: http://localhost:8000/admin/

Email verification is required for new accounts. In development,
verification emails are printed to the Docker console output.
```

## Architecture Notes

Read `references/architecture.md` for detailed architecture decisions if needed.

## Important Details

- **Always create the custom User model first** - Django does not support changing AUTH_USER_MODEL after the first migration
- **Never hardcode secrets** - all sensitive values come from environment variables
- **The entrypoint.sh uses pg_advisory_lock** to prevent migration race conditions when multiple containers start simultaneously
- **Tailwind CSS uses the standalone CLI** - no Node.js dependency anywhere in the stack
- **django-allauth handles all auth flows** - login, signup, logout, password reset, email verification
- **Email verification is mandatory** - in development, emails print to the console
