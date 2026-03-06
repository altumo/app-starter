# Execution Plan: Refactor starter-django to Pure Django

## Overview

Refactor the `starter-django` skill from a two-container Django+React architecture to a single-container pure Django architecture. Replace React/Vite/Node.js frontend with Django templates + Tailwind CSS v4 (standalone CLI). Replace Clerk auth with django-allauth. Remove DRF, CORS, nginx. Flatten project structure.

## Goals

1. Eliminate the separate React/Vite/Node.js frontend
2. Replace Clerk with django-allauth (email/password auth)
3. Single container: Django + Gunicorn (+ PostgreSQL as separate DB service)
4. Flatten project structure (no `backend/` subdirectory)
5. Keep: split settings, custom User model, pg_advisory_lock, health check, WhiteNoise, multi-stage Docker
6. Update all documentation (SKILL.md, READMEs, architecture.md)

## Architecture

- **Auth**: django-allauth (session-based, email-only, no username)
- **Templates**: Django template engine + Tailwind CSS v4
- **CSS Build**: Tailwind standalone CLI (no Node.js)
- **Static Files**: WhiteNoise (same as before)
- **Container**: Single `web` service + PostgreSQL
- **Views**: Function-based views with `@login_required`

## Execution Steps

All paths relative to `skills/starter-django/`.

### Phase 1: Delete Old Files

#### Step 1.1: Remove frontend directory
**Objective**: Delete the entire React/Vite frontend
**Details**: Delete `assets/templates/frontend/` and all its contents.
**Quality Criteria**: Directory no longer exists.

#### Step 1.2: Remove Clerk/DRF files from backend
**Objective**: Remove files that are being replaced
**Details**: Delete these files from `assets/templates/backend/`:
- `apps/accounts/authentication.py`
- `apps/accounts/serializers.py`
- `apps/accounts/views.py`
- `apps/accounts/urls.py`
- `apps/core/urls.py`
**Quality Criteria**: Files no longer exist.

#### Step 1.3: Remove docker-compose.prod.yml
**Objective**: Remove the separate prod compose file
**Details**: Delete `assets/templates/docker-compose.prod.yml`.
**Quality Criteria**: File no longer exists.

### Phase 2: Flatten Project Structure

#### Step 2.1: Move backend files to root
**Objective**: Eliminate the `backend/` subdirectory
**Details**: Move all files from `assets/templates/backend/` to `assets/templates/`. This includes:
- `manage.py`, `requirements.txt`, `Dockerfile`, `entrypoint.sh`, `gunicorn.conf.py`
- `config/` directory (settings, urls, wsgi, asgi)
- `apps/` directory (accounts, core)
Then delete the empty `assets/templates/backend/` directory.
**Quality Criteria**: No `backend/` directory exists. All files at root of `assets/templates/`.

### Phase 3: Create New Files

#### Step 3.1: Create pages app
**Objective**: Add the new pages app for template views
**Details**: Create `assets/templates/apps/pages/` with:

`apps/pages/__init__.py` — empty file

`apps/pages/apps.py`:
```python
from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"
    verbose_name = "Pages"
```

`apps/pages/views.py`:
```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home(request):
    """Public home page."""
    return render(request, "pages/home.html")


@login_required
def dashboard(request):
    """Protected dashboard page. Requires authentication."""
    return render(request, "pages/dashboard.html")
```

#### Step 3.2: Create Django templates
**Objective**: Create all HTML templates
**Details**: Create `assets/templates/templates/` directory with all templates.

`templates/base.html` — master layout with nav, messages, Tailwind CSS link. Nav shows Sign In/Sign Up for anonymous, email + Sign Out for authenticated. Sign Out is a POST form with CSRF token.

`templates/pages/home.html` — extends base.html, centered project name, sign-in/sign-up buttons for anonymous, dashboard link for authenticated.

`templates/pages/dashboard.html` — extends base.html, welcome card with user email.

See template-ui-analysis.md for exact contents.

#### Step 3.3: Create allauth template overrides
**Objective**: Style allauth pages with Tailwind
**Details**: Create `assets/templates/templates/allauth/` with:

`allauth/layouts/base.html` — extends project base.html, centers content in max-w-md container.

Element overrides in `allauth/elements/`:
- `button.html` — primary/secondary/danger/link variants with Tailwind classes
- `field.html` — label + widget + errors + help text
- `form.html` — CSRF token + body + actions slots
- `h1.html`, `h2.html` — styled headings
- `hr.html` — decorative divider with "or" text
- `alert.html` — error/success/warning/info variants
- `panel.html` — card container with title/body/actions
- `p.html` — styled paragraph

See template-ui-analysis.md for exact contents.

#### Step 3.4: Create Tailwind input.css
**Objective**: Set up Tailwind CSS v4 source file
**Details**: Create `assets/templates/static/css/input.css`:
```css
@import "tailwindcss" source("../../");

@theme {
  --color-primary-50: oklch(0.97 0.02 250);
  --color-primary-100: oklch(0.94 0.04 250);
  --color-primary-500: oklch(0.55 0.20 250);
  --color-primary-600: oklch(0.48 0.20 250);
  --color-primary-700: oklch(0.40 0.18 250);
  --color-primary-900: oklch(0.25 0.10 250);
}
```

### Phase 4: Modify Existing Files

#### Step 4.1: Rewrite settings/base.py
**Objective**: Update Django settings for allauth, remove DRF/CORS/Clerk
**Details**: See analysis-django-architect.md section 2 for exact contents.
Key changes:
- Remove: rest_framework, corsheaders, Clerk config, REST_FRAMEWORK dict
- Add: allauth, allauth.account, apps.pages, AccountMiddleware, AUTHENTICATION_BACKENDS
- Add: TEMPLATES DIRS, STATICFILES_DIRS, ACCOUNT_* settings, LOGIN_REDIRECT_URL
- Keep: WhiteNoise, dj-database-url, AUTH_USER_MODEL, password validators, logging

#### Step 4.2: Update settings/development.py
**Objective**: Remove CORS from dev settings
**Details**: Remove `CORS_ALLOW_ALL_ORIGINS = True`. Keep everything else.

#### Step 4.3: Rewrite settings/production.py
**Objective**: Remove CORS, add email config
**Details**: Remove CORS settings. Add EMAIL_BACKEND SMTP config with decouple env vars. See analysis section 4.

#### Step 4.4: Rewrite config/urls.py
**Objective**: New URL scheme with allauth, page views, health check
**Details**:
```python
from django.contrib import admin
from django.urls import include, path

from apps.core.views import health_check
from apps.pages.views import home, dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("health/", health_check, name="health"),
    path("dashboard/", dashboard, name="dashboard"),
    path("", home, name="home"),
]
```

#### Step 4.5: Rewrite User model (AbstractBaseUser)
**Objective**: Email-only user model, no clerk_id, no username
**Details**: Switch from AbstractUser to AbstractBaseUser + PermissionsMixin. Remove clerk_id field. Add explicit is_active, is_staff, date_joined fields. Set REQUIRED_FIELDS = []. See analysis section 6.

#### Step 4.6: Rewrite UserManager
**Objective**: Simplify manager, remove Clerk method
**Details**: Switch from UserManager to BaseUserManager. Remove get_or_create_from_clerk(). Remove username params. Rename to UserManager. See analysis section 6.

#### Step 4.7: Rewrite admin.py
**Objective**: Custom fieldsets for email-only User model
**Details**: Custom fieldsets/add_fieldsets without username. Remove clerk_id references. Add readonly_fields for date_joined/last_login. See analysis section 9.

#### Step 4.8: Rewrite core/views.py
**Objective**: Replace DRF health check with plain Django view
**Details**:
```python
from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint for load balancers and monitoring."""
    health = {"status": "healthy", "checks": {}}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health["checks"]["database"] = "ok"
    except Exception:
        health["status"] = "unhealthy"
        health["checks"]["database"] = "unavailable"
    status_code = 200 if health["status"] == "healthy" else 503
    return JsonResponse(health, status=status_code)
```

#### Step 4.9: Rewrite requirements.txt
**Objective**: Swap dependencies
**Details**:
```
Django>=5.2,<5.3
django-allauth>=65.14,<66
dj-database-url>=2.3,<3
gunicorn>=23,<24
whitenoise>=6.8,<7
psycopg[binary]>=3.2,<4
python-decouple>=3.8,<4
```

### Phase 5: Docker & DevOps

#### Step 5.1: Rewrite Dockerfile
**Objective**: Three-stage build with Tailwind CLI
**Details**: See container-architecture.md section 1. Three stages:
1. `debian:bookworm-slim` — download Tailwind binary, build CSS
2. `python:3.12-slim` — install Python deps
3. `python:3.12-slim` — runtime with app + CSS + deps
Health check URL: `/health/` (not `/api/health/`)

#### Step 5.2: Rewrite docker-compose.yml
**Objective**: Two services (db + web), Tailwind watch in dev
**Details**: See container-architecture.md section 2. Key: `web` service downloads Tailwind binary, runs `tailwindcss --watch &` in background + `runserver` in foreground. Uses volumes for pip_cache and tailwind_bin.

#### Step 5.3: Rewrite start-local-dev.sh
**Objective**: Simplified one-command setup
**Details**: Remove frontend/.env.local handling, Clerk prompts. Add startup URL hints. See container-architecture.md section 5.

#### Step 5.4: Rewrite .env.example
**Objective**: Remove Clerk/CORS/frontend vars, add email vars
**Details**: See container-architecture.md section 7.

#### Step 5.5: Rewrite .gitignore
**Objective**: Remove Node.js, add Tailwind output
**Details**: Remove Node.js section, frontend/ refs, backend/ prefix. Add `static/css/tailwind.css`. See container-architecture.md section 8.

### Phase 6: Documentation

#### Step 6.1: Rewrite SKILL.md
**Objective**: Update skill instructions for pure Django architecture
**Details**: Update description, instructions for scaffolding. Remove all React/Vite/frontend references. Update project structure diagram. Update next steps (no Clerk keys, no frontend/.env.local).

#### Step 6.2: Rewrite README.md (skill)
**Objective**: Update skill README
**Details**: Update "What You Get" structure, stack table, setup instructions. Remove Clerk, frontend references.

#### Step 6.3: Rewrite references/architecture.md
**Objective**: Document new architecture decisions
**Details**: Replace Clerk/CORS/proxy/React sections with allauth/Tailwind/Django template decisions.

#### Step 6.4: Rewrite templates/README.md (generated project)
**Objective**: Update generated project README
**Details**: Single-service architecture, django-allauth setup, no Clerk keys needed.

### Phase 7: Verification

#### Step 7.1: Verify file structure
**Objective**: Confirm all files exist and old files are removed
**Details**: Run `find skills/starter-django/assets/templates -type f | sort` and verify against expected structure.

#### Step 7.2: Verify no stale references
**Objective**: Confirm no React/Clerk/DRF/CORS references remain
**Details**: Grep for `clerk`, `react`, `vite`, `rest_framework`, `corsheader`, `frontend` in all skill files.

## File Structure (after execution)

```
skills/starter-django/
  SKILL.md
  README.md
  references/
    architecture.md
  assets/
    templates/
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
        __init__.py
        settings/
          __init__.py
          base.py
          development.py
          production.py
        urls.py
        wsgi.py
        asgi.py
      apps/
        __init__.py
        accounts/
          __init__.py
          models.py
          managers.py
          admin.py
          apps.py
        core/
          __init__.py
          views.py
          apps.py
        pages/
          __init__.py
          views.py
          apps.py
      templates/
        base.html
        pages/
          home.html
          dashboard.html
        allauth/
          layouts/
            base.html
          elements/
            button.html
            field.html
            form.html
            h1.html
            h2.html
            hr.html
            alert.html
            panel.html
            p.html
      static/
        css/
          input.css
```
