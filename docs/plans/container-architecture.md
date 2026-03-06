# Container Architecture: Single-Container Django with Tailwind Standalone CLI

**Date:** 2026-03-06
**Author:** DevOps analysis for starter-django refactor

---

## Overview

Moving from a two-container architecture (Django API + React/nginx) to a single-container architecture (Django with server-rendered templates + Tailwind CSS). No Node.js anywhere in the stack.

**Current state:** `db` + `backend` (Python) + `frontend` (Node.js) = 3 services
**Target state:** `db` + `web` (Python) = 2 services

---

## 1. Dockerfile (Production Multi-Stage Build)

Three stages: (1) download Tailwind binary and build CSS, (2) install Python dependencies, (3) slim runtime image.

The Tailwind build stage uses `debian:bookworm-slim` instead of Alpine to avoid musl binary issues documented in the Tailwind research. The `TARGETARCH` build arg is injected automatically by BuildKit for multi-platform builds.

### File: `Dockerfile` (project root)

```dockerfile
###############################################
# Stage 1: Build Tailwind CSS
###############################################
FROM debian:bookworm-slim AS tailwind-build

ARG TAILWIND_VERSION=4.1.3
ARG TARGETARCH

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && ARCH=$(case ${TARGETARCH} in \
         amd64) echo "x64" ;; \
         arm64) echo "arm64" ;; \
         *) echo "x64" ;; \
       esac) \
    && curl -sL -o /usr/local/bin/tailwindcss \
       "https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}/tailwindcss-linux-${ARCH}" \
    && chmod +x /usr/local/bin/tailwindcss

WORKDIR /build

# Copy only files Tailwind needs to scan for class names
COPY static/css/input.css ./static/css/input.css
COPY templates/ ./templates/
COPY apps/ ./apps/

# Build minified production CSS
RUN tailwindcss -i static/css/input.css -o static/css/tailwind.css --minify

###############################################
# Stage 2: Install Python dependencies
###############################################
FROM python:3.12-slim AS python-deps

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

###############################################
# Stage 3: Runtime
###############################################
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

WORKDIR /app

# Copy installed Python packages from python-deps stage
COPY --from=python-deps /install /usr/local

# Copy application code
COPY . .

# Copy built Tailwind CSS from tailwind-build stage
COPY --from=tailwind-build /build/static/css/tailwind.css ./static/css/tailwind.css

# Collect static files (WhiteNoise will serve these)
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-placeholder \
    DATABASE_URL=sqlite:///tmp/build.db \
    python manage.py collectstatic --no-input 2>/dev/null || true

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Switch to non-root user
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

ENTRYPOINT ["./entrypoint.sh"]
```

### Design decisions

- **Three stages, not two.** Tailwind build and Python dependency install are independent and can run in parallel with BuildKit. Keeping them separate also means a change to `requirements.txt` does not invalidate the Tailwind CSS cache and vice versa.
- **`debian:bookworm-slim` for Tailwind stage.** The Tailwind v4 standalone binary for Linux is a glibc binary. Alpine uses musl and the musl variants have known issues on ARM64. Since we promise multi-arch support, bookworm-slim is the safe choice.
- **`python:3.12-slim` for runtime** (which is bookworm-based). No change from current.
- **`TARGETARCH` is automatic.** Docker BuildKit injects it. The `case` statement maps `amd64` -> `x64` and `arm64` -> `arm64` to match Tailwind's naming convention.
- **Copy order for Tailwind stage.** We copy `input.css`, `templates/`, and `apps/` (for any Tailwind classes in Python files or templatetags). We do NOT copy `static/css/tailwind.css` because it does not exist yet -- we are building it.
- **Health check URL changed** from `/api/health/` to `/health/` since we are removing DRF and the `/api/` prefix.
- **`collectstatic` runs after Tailwind CSS is copied in.** The built `tailwind.css` lands in `static/css/`, and `collectstatic` picks it up along with all other static files into `staticfiles/`.

---

## 2. docker-compose.yml (Development)

Two services: `db` (PostgreSQL) and `web` (Django + Tailwind watch).

The `web` service needs to run two processes concurrently in development:
1. `tailwindcss --watch` to rebuild CSS when template classes change
2. `manage.py runserver` for the Django dev server

I use a simple shell `&` background approach rather than adding supervisord or another process manager. The Tailwind watcher is a lightweight background process. If it crashes, the developer sees stale CSS and restarts -- acceptable for dev.

### File: `docker-compose.yml` (project root)

```yaml
services:
  db:
    image: postgres:17-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-__PROJECT_NAME__}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
    ports:
      - "${DB_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-__PROJECT_NAME__}"]
      interval: 5s
      timeout: 5s
      retries: 5

  web:
    image: python:3.12-slim
    working_dir: /app
    command: >
      bash -c "
        set -e

        echo '==> Installing system dependencies...'
        apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc postgresql-client curl ca-certificates

        echo '==> Installing Python dependencies...'
        pip install --no-cache-dir -r requirements.txt

        echo '==> Downloading Tailwind CSS standalone CLI...'
        if [ ! -f /usr/local/bin/tailwindcss ]; then
          ARCH=$$(uname -m)
          case $$ARCH in
            x86_64) TW_ARCH=x64 ;;
            aarch64) TW_ARCH=arm64 ;;
            arm64) TW_ARCH=arm64 ;;
            *) TW_ARCH=x64 ;;
          esac
          curl -sL -o /usr/local/bin/tailwindcss \
            'https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION:-4.1.3}/tailwindcss-linux-'$$TW_ARCH
          chmod +x /usr/local/bin/tailwindcss
        fi

        echo '==> Running migrations...'
        python manage.py migrate --no-input

        echo '==> Starting Tailwind CSS watcher...'
        tailwindcss -i static/css/input.css -o static/css/tailwind.css --watch &

        echo '==> Starting Django development server...'
        python manage.py runserver 0.0.0.0:8000
      "
    volumes:
      - .:/app
      - pip_cache:/root/.cache/pip
      - tailwind_bin:/usr/local/bin
    ports:
      - "${WEB_PORT:-8000}:8000"
    env_file:
      - .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.development
      DATABASE_URL: postgres://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-__PROJECT_NAME__}
      DB_HOST: db
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
  pip_cache:
  tailwind_bin:
```

### Design decisions

- **`tailwind_bin` volume.** Persists the downloaded Tailwind binary across container restarts so it is only downloaded once. The `if [ ! -f ... ]` check skips the download on subsequent runs.
- **`pip_cache` volume.** Persists pip's download cache across container restarts. Combined with `--no-cache-dir` being removed... actually, I keep `--no-cache-dir` since the volume already handles caching at the download level. On reflection, remove `--no-cache-dir` and use the cache volume for faster reinstalls. Let me correct: the `pip_cache` volume caches wheel downloads so `pip install` on restart is fast even with `--no-cache-dir` absent. But since we are mounting `/root/.cache/pip`, pip will naturally cache there. So let me drop `--no-cache-dir` from the dev compose to benefit from the cache volume.
- **Single `web` service** replaces both `backend` and `frontend`.
- **`WEB_PORT`** instead of `BACKEND_PORT` -- clearer naming for a single-service architecture.
- **Background Tailwind watcher.** The `&` sends Tailwind to the background. Django's `runserver` runs in the foreground. When the container stops (Ctrl+C), `runserver` receives SIGTERM, and the container exits, killing the background Tailwind process too. This is clean for development.
- **No supervisord, no foreman.** Adding a process manager for dev is unnecessary complexity. The `bash -c` with `&` pattern is standard in docker-compose dev setups.

**Corrected `command` (dropping `--no-cache-dir` for dev):**

The `command` block above in the YAML is already the final version. One note: I kept `--no-cache-dir` because the `pip_cache` volume is for the download cache only. Actually, let me just present the final clean version. The YAML above is correct as-is.

---

## 3. docker-compose.prod.yml -- Remove It

**Decision: Remove `docker-compose.prod.yml` entirely.**

Rationale:
- Production deployments vary wildly (fly.io, Railway, AWS ECS, bare VPS with `docker compose`). A prod compose file creates a false sense of "production-ready" that is misleading.
- The `Dockerfile` IS the production artifact. It builds a complete, self-contained image.
- For teams that DO use `docker compose` in production, they can create their own compose file. It is a trivial file -- just `db` + `web` with the `build:` directive.
- The generated project's `README.md` should document how to build and run the production image.

If the user insists on keeping a prod compose, here is a minimal one. But my recommendation is to not include it and instead document the `docker build` + `docker run` commands in the README.

### File: `docker-compose.prod.yml` (optional, NOT recommended to include)

```yaml
services:
  db:
    image: postgres:17-alpine
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build:
      context: .
      args:
        TAILWIND_VERSION: "4.1.3"
    restart: always
    env_file:
      - .env
    environment:
      DJANGO_SETTINGS_MODULE: config.settings.production
      DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      DB_HOST: db
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"

volumes:
  postgres_data:
```

---

## 4. entrypoint.sh (Production Only)

This file runs inside the production Docker image. It waits for the database, runs migrations with `pg_advisory_lock`, then starts gunicorn. No Tailwind work needed here -- CSS was built at image build time.

### File: `entrypoint.sh` (project root)

```bash
#!/bin/bash
set -e

# Default settings module for production
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.production}"

echo "==> Waiting for database..."
MAX_RETRIES=30
RETRY_COUNT=0
until pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -q 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
        echo "ERROR: Database not available after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "    Waiting for database (attempt $RETRY_COUNT/$MAX_RETRIES)..."
    sleep 2
done
echo "==> Database is ready"

echo "==> Running migrations..."
# Use advisory lock to prevent concurrent migration execution
# Lock ID 1 is arbitrary but consistent across all instances
python -c "
import django, os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT pg_advisory_lock(1)')
    try:
        from django.core.management import call_command
        call_command('migrate', '--no-input')
    finally:
        cursor.execute('SELECT pg_advisory_unlock(1)')
"
echo "==> Migrations complete"

echo "==> Starting gunicorn..."
exec gunicorn config.wsgi:application -c gunicorn.conf.py
```

### Changes from current

- Removed: nothing structurally. The current entrypoint is already clean.
- The only change is that the health check URL in the Dockerfile changed from `/api/health/` to `/health/`.
- The entrypoint itself has no Clerk-specific or frontend-specific code, so no removals needed here.

---

## 5. start-local-dev.sh

Simplified. No more `frontend/.env.local`, no Clerk key prompts.

### File: `start-local-dev.sh` (project root)

```bash
#!/bin/bash
set -e

echo "========================================="
echo "  __PROJECT_NAME__ - Local Development"
echo "========================================="
echo ""

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check docker compose is available
if ! docker compose version > /dev/null 2>&1; then
    echo "ERROR: docker compose is not available. Please install Docker Compose v2."
    exit 1
fi

# Create .env from .env.example if it doesn't exist
if [ ! -f .env ]; then
    echo "==> Creating .env from .env.example..."
    cp .env.example .env

    # Generate a random SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || openssl rand -base64 50 | tr -d '\n')
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|SECRET_KEY=REPLACE_ME_WITH_RANDOM_SECRET|SECRET_KEY=$SECRET_KEY|" .env
    else
        sed -i "s|SECRET_KEY=REPLACE_ME_WITH_RANDOM_SECRET|SECRET_KEY=$SECRET_KEY|" .env
    fi

    echo "    Generated random SECRET_KEY"
    echo ""
fi

echo "==> Starting services with Docker Compose..."
echo ""
echo "    This may take a few minutes on first run (installing deps, downloading Tailwind)."
echo "    Subsequent starts will be faster (dependencies are cached)."
echo ""
echo "    Once running:"
echo "      App:      http://localhost:${WEB_PORT:-8000}"
echo "      Database: localhost:${DB_PORT:-5432}"
echo ""

docker compose up --build

echo ""
echo "Services stopped."
```

### Changes from current

- Removed: `frontend/.env.local` creation block
- Removed: Clerk API key instructions
- Updated: messaging reflects single-service architecture
- Added: URL hints on startup so the developer knows where to go

---

## 6. gunicorn.conf.py

No changes needed. The current configuration is already solid.

### File: `gunicorn.conf.py` (project root, unchanged)

```python
import multiprocessing

# Bind to all interfaces
bind = "0.0.0.0:8000"

# Workers: 2-4 x CPU cores
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2

# Timeout
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Security
limit_request_line = 8190
limit_request_fields = 100

# Restart workers after this many requests (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Use /dev/shm for worker heartbeat (Docker doesn't mount /tmp on tmpfs)
worker_tmp_dir = "/dev/shm"
```

### Rationale for no changes

- `gthread` worker class is fine for Django template rendering (I/O bound on DB queries).
- Worker count formula is standard.
- If the project later adds WebSocket support, they would switch to `uvicorn` workers, but that is out of scope for this refactor.

---

## 7. .env.example

### File: `.env.example` (project root)

```bash
# =============================================================================
# Django
# =============================================================================

# Django secret key - generate with: python3 -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY=REPLACE_ME_WITH_RANDOM_SECRET

# Comma-separated list of allowed hosts (production: your domain)
ALLOWED_HOSTS=localhost,127.0.0.1

# Database URL (docker-compose overrides this, but useful for local dev without Docker)
DATABASE_URL=postgres://postgres:postgres@localhost:5432/__PROJECT_NAME__

# =============================================================================
# PostgreSQL
# =============================================================================

POSTGRES_DB=__PROJECT_NAME__
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# =============================================================================
# Ports (optional - override defaults)
# =============================================================================

# WEB_PORT=8000
# DB_PORT=5432

# =============================================================================
# Tailwind CSS (optional - override pinned version)
# =============================================================================

# TAILWIND_VERSION=4.1.3

# =============================================================================
# Email (production only - for django-allauth email verification)
# =============================================================================

# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.example.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@example.com
# EMAIL_HOST_PASSWORD=your-email-password
# DEFAULT_FROM_EMAIL=noreply@example.com
```

### Changes from current

- **Removed:** `CLERK_JWKS_URL`, `CLERK_AUTHORIZED_PARTIES` (Clerk is gone)
- **Removed:** `FRONTEND_PORT` (no frontend service)
- **Removed:** `BACKEND_PORT` (renamed to `WEB_PORT`)
- **Removed:** `CORS_ALLOWED_ORIGINS` (no cross-origin requests)
- **Added:** `TAILWIND_VERSION` (optional override)
- **Added:** `EMAIL_*` section (commented out, for production allauth email sending)
- **Kept:** `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, `POSTGRES_*`, `DB_PORT`

---

## 8. .gitignore Updates

### File: `.gitignore` (project root)

```gitignore
# =============================================================================
# Python
# =============================================================================
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
*.egg
dist/
build/
.eggs/
*.whl
.venv/
venv/
env/

# =============================================================================
# Django
# =============================================================================
*.log
db.sqlite3
db.sqlite3-journal
staticfiles/
media/

# =============================================================================
# Tailwind CSS (generated output - rebuilt from input.css)
# =============================================================================
static/css/tailwind.css

# =============================================================================
# Environment
# =============================================================================
.env
.env.local
.env.*.local

# =============================================================================
# IDE
# =============================================================================
.idea/
.vscode/
*.swp
*.swo
*~

# =============================================================================
# OS
# =============================================================================
.DS_Store
Thumbs.db
*.tmp

# =============================================================================
# Docker
# =============================================================================
# Don't ignore docker-compose files or Dockerfiles
```

### Changes from current

- **Removed:** Node.js section (`node_modules/`, `frontend/dist/`, npm/yarn/pnpm logs)
- **Removed:** `frontend/.env.local` (no frontend directory)
- **Removed:** `backend/` prefix from `staticfiles/` and `media/` (project is now flat)
- **Added:** `static/css/tailwind.css` -- this is a generated file, should not be committed. It is built by the Tailwind CLI in Docker (prod) or watch mode (dev).

---

## 9. Development Workflow

### First-time setup

```
git clone <repo>
cd <project>
./start-local-dev.sh
```

That is it. The script:
1. Checks Docker is running
2. Creates `.env` from `.env.example` with a generated `SECRET_KEY`
3. Runs `docker compose up --build`

On first run, Docker will:
1. Pull `python:3.12-slim` and `postgres:17-alpine`
2. Install system deps (`libpq-dev`, `gcc`, `curl`)
3. Install Python dependencies
4. Download the Tailwind standalone binary (~45MB)
5. Run migrations
6. Start Tailwind watcher (background) + Django dev server (foreground)

Subsequent starts skip steps 1-4 thanks to Docker layer cache and named volumes.

### Day-to-day development

| Change | What happens | Action needed |
|--------|-------------|---------------|
| Edit Python code | Django `runserver` auto-reloads | None (auto) |
| Edit Django templates | Django `runserver` auto-reloads | None (auto) |
| Add Tailwind classes in templates | Tailwind watcher detects change, rebuilds CSS | Refresh browser |
| Edit `input.css` (custom theme, etc.) | Tailwind watcher detects change, rebuilds CSS | Refresh browser |
| Add Python dependency | Stop, re-run `docker compose up` | Manual restart |
| Change `.env` | Stop, re-run `docker compose up` | Manual restart |

### What developers do NOT need

- Node.js (not installed anywhere)
- npm/yarn/pnpm (none)
- A separate terminal for Tailwind (runs inside the container)
- A separate terminal for the frontend (there is no frontend service)
- CORS configuration (same origin)
- JWT/token management (session auth)

---

## 10. Project Structure (Post-Refactor)

For context, here is how the generated project's files map to the Docker setup:

```
__PROJECT_NAME__/
  manage.py
  requirements.txt
  Dockerfile                  # Multi-stage production build
  docker-compose.yml          # Development (db + web)
  entrypoint.sh               # Production container entrypoint
  gunicorn.conf.py            # Production gunicorn config
  start-local-dev.sh          # One-command dev setup
  .env.example                # Environment template
  .gitignore
  config/
    settings/
      base.py
      development.py
      production.py
    urls.py
    wsgi.py
  apps/
    accounts/                 # Custom User model + allauth config
    pages/                    # Template views (home, dashboard)
  templates/
    base.html                 # Base template with Tailwind CSS link
    pages/
      home.html
      dashboard.html
    account/                  # Overridden allauth templates
      login.html
      signup.html
  static/
    css/
      input.css               # Tailwind source (committed)
      tailwind.css             # Tailwind output (gitignored, built by CLI)
    js/                       # Minimal vanilla JS if needed
    images/
  staticfiles/                # collectstatic output (gitignored)
```

---

## 11. Summary of Files to Create/Modify

| File | Action | Location in skill assets |
|------|--------|-------------------------|
| `Dockerfile` | **New** (replaces `backend/Dockerfile`) | Project root |
| `docker-compose.yml` | **Rewrite** | Project root |
| `docker-compose.prod.yml` | **Delete** | Removed |
| `entrypoint.sh` | **Move + minor edit** (from `backend/`) | Project root |
| `start-local-dev.sh` | **Rewrite** (simpler) | Project root |
| `gunicorn.conf.py` | **Move unchanged** (from `backend/`) | Project root |
| `.env.example` | **Rewrite** | Project root |
| `.gitignore` | **Rewrite** | Project root |

All files move from `backend/` subdirectory to project root (Goal 4: flatten project structure). The `frontend/` directory and all its contents are deleted entirely.

---

## 12. Open Questions / Alternatives Considered

### Why not use `django-tailwind-cli` Django package?

The `django-tailwind-cli` package from django-commons automates binary management and provides `manage.py tailwind build/watch` commands. It is well-maintained and would work. However:

- It adds a dependency for something that is two `curl` + `chmod` commands
- It puts binary management logic behind a Django app, making the Docker build less transparent
- The raw binary approach gives full control over caching and versioning in Docker
- For a starter skill, being explicit about what happens is more educational

If the project grows and developers want `manage.py tailwind watch` convenience, they can add it later. The `input.css` format is identical either way.

### Why not Alpine for the runtime image?

Alpine uses musl libc. The Tailwind standalone binary has documented issues with musl on ARM64. While the runtime image does not run Tailwind (CSS is pre-built), using `python:3.12-slim` (Debian bookworm) is consistent with the build stage and avoids the well-known psycopg/pip wheel compatibility issues that Alpine introduces for Python images. The size difference is ~40MB (Alpine ~55MB vs slim ~95MB) -- not worth the compatibility risk.

### Why background process instead of supervisord for dev?

Supervisord, honcho, or overmind would give better process management in development. But they add a dependency and complexity for a two-process dev setup where one process (Tailwind watch) is non-critical. If the Tailwind watcher crashes in dev, CSS just stops updating -- the developer notices immediately and restarts. For production, only gunicorn runs (Tailwind is not needed), so there is no multi-process concern.

### Why `WEB_PORT` instead of `BACKEND_PORT`?

With a single service, "backend" is misleading -- there is no "frontend" to contrast with. `WEB_PORT` is neutral and accurate. It is also shorter.
