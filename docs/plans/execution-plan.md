# Execution Plan: Django + Next.js + Postgres + Clerk + Docker Bootstrap Skill

## Overview

Build a Claude Code skill (`starter-django`) that bootstraps a production-ready full-stack project. When invoked, the skill instructs Claude to generate a complete project scaffold with Django backend API, Next.js frontend, PostgreSQL database, Clerk authentication, and Docker containerization - all wired together with turn-key local development.

## Goals

1. Create a Claude Code skill with SKILL.md + bundled scripts/templates
2. Git repo initialization with proper .gitignore
3. Django backend with custom User model, DRF, Clerk JWT auth, health checks
4. Next.js frontend with App Router, TypeScript, Clerk, API proxy to Django
5. Docker Compose for local dev (Postgres + Django + Next.js, single command)
6. Production Dockerfiles with safe migration execution
7. .env-based configuration with sensible defaults
8. start-local-dev.sh for turn-key setup

## Architecture

```
project-root/
├── backend/                    # Django project
│   ├── config/                 # Django settings module
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── accounts/           # Custom User model + Clerk auth
│   │   └── core/               # Health check, common utilities
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── gunicorn.conf.py
├── frontend/                   # Next.js project
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── middleware.ts
│   ├── Dockerfile
│   ├── next.config.ts
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml          # Local development
├── docker-compose.prod.yml     # Production reference
├── .env.example                # Documented env vars
├── .env                        # Local defaults (git-ignored)
├── .gitignore
├── start-local-dev.sh
└── README.md
```

### Key Decisions

1. **Django settings**: Split settings (base/development/production) - cleaner than single file with many conditionals
2. **Clerk auth in Django**: Use `PyJWT` + JWKS verification (custom DRF auth class) - avoids dependency on `clerk-django` which is young and may change; gives full control
3. **API proxy**: Next.js `rewrites` in `next.config.ts` to proxy `/api/*` to Django - eliminates CORS issues in dev
4. **Django CORS**: `django-cors-headers` configured for production use when frontend calls Django directly
5. **Migrations**: Entrypoint script with `pg_isready` wait + advisory lock for safe concurrent migration
6. **Custom User model**: Created from day one (cannot change later)
7. **Static files**: WhiteNoise in Django for simplicity
8. **Database**: `dj-database-url` for DATABASE_URL parsing

### Version Pinning

| Component | Version | Rationale |
|-----------|---------|-----------|
| Python | 3.12 | Stable, broad compatibility |
| Django | 5.2.x | LTS until April 2028 |
| PostgreSQL | 17 | Latest stable |
| Node.js | 22 | LTS |
| Next.js | latest (16.x) | Via create-next-app |
| @clerk/nextjs | latest (7.x) | Via npm install |
| TypeScript | 5.x | Stable |

## Execution Steps

### Phase 1: Skill Structure

#### Step 1.1: Create Skill Directory and SKILL.md
**Objective**: Create the skill file structure
**Details**:
- Create `.claude/skills/starter-django/SKILL.md` with frontmatter
- The SKILL.md contains full instructions for Claude to follow
- Create `scripts/` directory for helper templates

**Outputs**: SKILL.md file, scripts directory

#### Step 1.2: Create Template Scripts
**Objective**: Bundle reusable scripts and config templates
**Details**:
- `scripts/setup-backend.sh` - Django project creation + configuration
- `scripts/setup-frontend.sh` - Next.js project creation + Clerk setup
- `scripts/docker-compose.yml.template` - Docker compose template
- `scripts/entrypoint.sh.template` - Django Docker entrypoint
- `scripts/start-local-dev.sh.template` - Local dev startup script

**Outputs**: Template files in scripts/

### Phase 2: Django Backend Templates

#### Step 2.1: Django Settings
**Objective**: Create production-ready Django settings
**Details**:
- `base.py`: INSTALLED_APPS, MIDDLEWARE, AUTH_USER_MODEL, DRF config, CORS config
- `development.py`: DEBUG=True, CORS allow all, console email
- `production.py`: Security headers, HTTPS, proper ALLOWED_HOSTS

#### Step 2.2: Custom User Model
**Objective**: Custom User model that extends AbstractUser
**Details**:
- `apps/accounts/models.py` with CustomUser
- `apps/accounts/admin.py` with UserAdmin
- `apps/accounts/managers.py` with CustomUserManager

#### Step 2.3: Clerk Authentication
**Objective**: DRF authentication class for Clerk JWT verification
**Details**:
- `apps/accounts/authentication.py` with ClerkJWTAuthentication
- Uses PyJWT + JWKS for verification
- Validates `exp`, `iss`, `azp` claims
- Returns ClerkUser object for DRF compatibility

#### Step 2.4: API Endpoints
**Objective**: Core API structure
**Details**:
- Health check endpoint at `/api/health/`
- Auth status endpoint at `/api/auth/me/`
- URL configuration with API router

#### Step 2.5: Requirements
**Objective**: Pin all Python dependencies
**Details**:
```
Django>=5.2,<5.3
djangorestframework>=3.15,<4
django-cors-headers>=4.6,<5
dj-database-url>=2.3,<3
gunicorn>=23,<24
whitenoise>=6.8,<7
psycopg[binary]>=3.2,<4
PyJWT[crypto]>=2.11,<3
python-decouple>=3.8,<4
```

#### Step 2.6: Gunicorn Config
**Objective**: Production-ready gunicorn configuration
**Details**:
- Worker count based on CPU cores
- Graceful timeout
- Access logging
- Bind to 0.0.0.0:8000

### Phase 3: Next.js Frontend Templates

#### Step 3.1: Next.js Project Structure
**Objective**: App Router project with Clerk
**Details**:
- Root layout with ClerkProvider
- Middleware with clerkMiddleware + route matcher
- Sign-in/sign-up pages
- Dashboard page (protected)
- API client utility with token passing

#### Step 3.2: API Client
**Objective**: Typed API client for Django communication
**Details**:
- `lib/api.ts` with fetch wrapper
- Automatically attaches Clerk Bearer token
- Uses `/api/` prefix (proxied to Django)

#### Step 3.3: Next.js Config
**Objective**: Configure API proxying and build settings
**Details**:
- `next.config.ts` with rewrites to Django
- Output standalone for Docker

### Phase 4: Docker Configuration

#### Step 4.1: Django Dockerfile
**Objective**: Multi-stage production Dockerfile
**Details**:
- Stage 1 (builder): Install Python deps
- Stage 2 (runtime): Copy deps + code, collectstatic at build
- Non-root user
- Entrypoint script

#### Step 4.2: Django Entrypoint
**Objective**: Safe container startup script
**Details**:
- Wait for Postgres with pg_isready loop
- Run migrations with advisory lock (SELECT pg_advisory_lock)
- Start gunicorn
- Handle SIGTERM gracefully

#### Step 4.3: Next.js Dockerfile
**Objective**: Multi-stage production Dockerfile
**Details**:
- Stage 1: Install deps
- Stage 2: Build with standalone output
- Stage 3: Run with minimal image
- Non-root user

#### Step 4.4: Docker Compose (Dev)
**Objective**: Turn-key local development
**Details**:
- postgres service with health check, named volume
- backend service with volume mount, depends_on postgres
- frontend service with volume mount
- Shared .env file

#### Step 4.5: Docker Compose (Prod)
**Objective**: Production reference compose
**Details**:
- Uses built images
- No volume mounts
- Health checks on all services

### Phase 5: Developer Experience

#### Step 5.1: start-local-dev.sh
**Objective**: Single command to start development
**Details**:
- Check Docker is running
- Copy .env.example to .env if not exists
- Generate Django SECRET_KEY if not set
- docker compose up --build
- Print access URLs

#### Step 5.2: .env Files
**Objective**: Environment configuration
**Details**:
- `.env.example` with all vars documented
- `.env` with local defaults (git-ignored)
- Separate sections: Django, Database, Clerk, Frontend

#### Step 5.3: .gitignore
**Objective**: Comprehensive gitignore
**Details**: Python, Node.js, Docker, IDE, OS files, .env

#### Step 5.4: README
**Objective**: Getting started documentation
**Details**:
- Prerequisites
- Quick start (3 steps)
- Environment variables reference
- Project structure
- Development workflow
- Production deployment notes

## Quality Assurance

- All files must be syntactically valid
- Django settings must pass `manage.py check --deploy` in production mode
- Docker compose must start without errors
- All environment variables documented in .env.example
- No hardcoded secrets anywhere
- Non-root Docker users
- Health checks on all services

## Risk Register

| Risk | Mitigation |
|------|------------|
| Clerk SDK breaking changes | Pin versions, use manual PyJWT as primary (stable API) |
| Migration race condition | Advisory lock in entrypoint script |
| Database not ready | pg_isready loop with timeout and backoff |
| Port conflicts | Configurable via .env (default 8000, 3000, 5432) |
| create-next-app interactive prompts | Use --yes flag and explicit options |
| Python/Node version drift | Pin in Dockerfiles, document in README |

## File Structure (Final Skill)

```
.claude/skills/starter-django/
├── SKILL.md                        # Main skill instructions
├── scripts/
│   ├── create-project.sh           # Master orchestration script
│   └── wait-for-db.sh              # Database readiness check
├── references/
│   └── architecture.md             # Architecture decisions doc
└── assets/
    └── templates/                  # All file templates
        ├── backend/
        │   ├── requirements.txt
        │   ├── Dockerfile
        │   ├── entrypoint.sh
        │   ├── gunicorn.conf.py
        │   ├── config/
        │   │   ├── settings/
        │   │   │   ├── base.py
        │   │   │   ├── development.py
        │   │   │   └── production.py
        │   │   ├── urls.py
        │   │   ├── wsgi.py
        │   │   └── asgi.py
        │   └── apps/
        │       ├── accounts/
        │       │   ├── models.py
        │       │   ├── admin.py
        │       │   ├── managers.py
        │       │   ├── authentication.py
        │       │   ├── serializers.py
        │       │   ├── views.py
        │       │   ├── urls.py
        │       │   └── apps.py
        │       └── core/
        │           ├── views.py
        │           ├── urls.py
        │           └── apps.py
        ├── frontend/
        │   ├── Dockerfile
        │   ├── next.config.ts
        │   ├── src/
        │   │   ├── app/
        │   │   │   ├── layout.tsx
        │   │   │   ├── page.tsx
        │   │   │   ├── (auth)/
        │   │   │   │   ├── sign-in/[[...sign-in]]/page.tsx
        │   │   │   │   └── sign-up/[[...sign-up]]/page.tsx
        │   │   │   └── (dashboard)/
        │   │   │       ├── layout.tsx
        │   │   │       └── dashboard/page.tsx
        │   │   ├── components/
        │   │   │   └── providers.tsx
        │   │   ├── lib/
        │   │   │   └── api.ts
        │   │   └── middleware.ts
        │   └── .env.local.example
        ├── docker-compose.yml
        ├── docker-compose.prod.yml
        ├── .env.example
        ├── .gitignore
        ├── start-local-dev.sh
        └── README.md
```
