# starter-django

Scaffolds a production-ready Django project with **Django + PostgreSQL + Tailwind CSS + Docker**.

## What You Get

```
myapp/
├── config/                    # Split settings (base/dev/prod)
│   └── settings/
├── apps/
│   ├── accounts/              # Custom User model (email-based)
│   ├── core/                  # Health check endpoint
│   └── pages/                 # Home + dashboard views
├── templates/                 # Django templates + allauth overrides
│   ├── base.html              # Master layout with nav + messages
│   ├── pages/                 # Home, dashboard
│   └── allauth/               # Styled auth pages (Tailwind)
├── static/css/input.css       # Tailwind v4 source
├── Dockerfile                 # Multi-stage (Tailwind CLI + Python)
├── docker-compose.yml         # Dev: PostgreSQL + Django + Tailwind watch
├── start-local-dev.sh         # One-command setup
└── .env.example               # All configuration documented
```

~35 files. Zero manual setup. No Node.js required.

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

## Setup

### 1. Start

```bash
./start-local-dev.sh
```

That's it. The script handles everything: starts PostgreSQL, installs dependencies, downloads Tailwind CLI, runs migrations, and starts the dev server with CSS watch.

### 2. Access

| Service | URL |
|---------|-----|
| Home | http://localhost:8000 |
| Sign Up | http://localhost:8000/accounts/signup/ |
| Sign In | http://localhost:8000/accounts/login/ |
| Dashboard | http://localhost:8000/dashboard/ |
| Health Check | http://localhost:8000/health/ |
| Django Admin | http://localhost:8000/admin/ |

### 3. Email Verification

New accounts require email verification. In development, verification emails are printed to the Docker console output. Copy the verification link from the console to activate accounts.

## Common Tasks

```bash
# Django management commands
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Add Python packages
# Add to requirements.txt, then:
docker compose up --build web

# Logs
docker compose logs -f web

# Stop / reset
docker compose down        # stop
docker compose down -v     # stop + wipe database
```

## Architecture

- **Auth**: django-allauth with email/password (no username, social login ready)
- **User Model**: Custom `AbstractBaseUser` with email as identifier (set from day one)
- **Settings**: Split into `base.py`, `development.py`, `production.py`
- **Styling**: Tailwind CSS v4 standalone CLI (no Node.js anywhere)
- **Static Files**: WhiteNoise serves compressed files with cache headers
- **Migrations**: `pg_advisory_lock` prevents race conditions with multiple replicas
- **Container**: Single service (Django + Gunicorn) + PostgreSQL

See [references/architecture.md](references/architecture.md) for detailed rationale.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Database not available" | Docker Desktop might still be starting. Wait and retry. |
| Email verification not arriving | Check Docker console output — emails print to the terminal in dev. |
| Port conflict | Change port in `.env`: `WEB_PORT=8001` or `DB_PORT=5433` |
| CSS not updating | Tailwind watcher may have stopped. Restart: `docker compose restart web` |
