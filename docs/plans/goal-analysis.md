# Goal Analysis: Refactor starter-django to Pure Django

## Context

The `starter-django` skill currently scaffolds a **two-container** architecture:
- **Backend**: Django 5.2 + DRF + Gunicorn (Python container)
- **Frontend**: React 19 + Vite + TypeScript (Node.js container, nginx in prod)
- **Auth**: Clerk (React components frontend, PyJWT JWKS verification backend)
- **Proxy**: Vite dev proxy in dev, nginx reverse proxy in prod

The user wants to refactor this into a **single-container, all-Django** architecture using Django best patterns.

## Goals

### Goal 1: Eliminate the Separate Frontend
- Remove the entire `frontend/` directory (React, Vite, Node.js, nginx)
- Replace with Django templates for all HTML rendering
- Use Tailwind CSS v4 for styling (via standalone CLI — no Node.js runtime dependency)
- Keep the same pages: Home, Sign In, Sign Up, Dashboard

### Goal 2: Replace Clerk with Django-Native Auth
- Remove Clerk dependency (both backend PyJWT/JWKS and frontend @clerk/clerk-react)
- Replace with `django-allauth` — the standard Django auth package
- Support email/password auth out of the box, social login ready
- Use Django's built-in session auth (no JWT verification needed)
- Keep the custom User model (email as primary identifier)

### Goal 3: Single Container Architecture
- One Docker service: Django + Gunicorn (plus PostgreSQL as a separate DB service)
- Remove nginx entirely — WhiteNoise serves static files
- Remove CORS middleware — no cross-origin requests when everything is one app
- Simplify docker-compose to just `db` + `web` services

### Goal 4: Flatten Project Structure
- Remove the `backend/` subdirectory — Django project lives at the repo root
- Standard Django project layout: `manage.py` at root, `config/` for settings, `apps/` for Django apps
- Cleaner, more conventional Django structure

### Goal 5: Keep What Works
- Split settings (base/dev/prod)
- Custom User model from day one
- pg_advisory_lock for safe migrations
- Health check endpoint
- Multi-stage Docker build
- Gunicorn with sensible production config
- WhiteNoise for static files
- python-decouple for env config

### Goal 6: Update All Documentation
- Rewrite SKILL.md for the new architecture
- Rewrite README.md (skill README)
- Rewrite templates/README.md (generated project README)
- Rewrite references/architecture.md
- Update .env.example (remove Clerk, frontend vars)
- Update .gitignore (remove Node.js/frontend sections)

## What Gets Removed
- `assets/templates/frontend/` — entire directory
- `frontend/.env.local.example`
- `nginx.conf`
- `frontend/Dockerfile`
- `docker-compose.prod.yml` — merge into single docker-compose with profiles or simplify
- `django-cors-headers` dependency
- `PyJWT[crypto]` dependency
- `djangorestframework` dependency (replaced by standard Django views)
- Clerk configuration (CLERK_JWKS_URL, CLERK_AUTHORIZED_PARTIES, etc.)
- `apps/accounts/authentication.py` (ClerkJWTAuthentication)
- `apps/accounts/serializers.py` (DRF serializer)

## What Gets Added
- `django-allauth` for authentication
- Django templates (base.html, home.html, dashboard.html, etc.)
- Tailwind CSS v4 via standalone CLI (build step in Docker, watch in dev)
- `apps/pages/` — new app for template views (home, dashboard)
- Static files structure (`static/css/`, `static/js/`)
- Template inheritance structure (`templates/base.html`, etc.)

## Key Decisions to Make
1. **Tailwind CSS integration**: Standalone CLI (no Node.js) vs django-tailwind (requires Node.js)
   - Decision: Standalone CLI to keep the stack truly Python-only
2. **Keep DRF or not**: Pure Django views vs keeping DRF for potential API
   - Decision: Remove DRF. Use Django views + Django forms. Users can add DRF later if needed.
3. **Template styling approach**: Tailwind utility classes in templates
   - Decision: Use Tailwind v4 with `@import "tailwindcss"` in input.css
4. **Auth flow**: django-allauth handles login/signup/logout with its own templates
   - Decision: Override allauth templates with custom styled versions
