# __PROJECT_NAME__

Web application built with Django + PostgreSQL + Tailwind CSS + Docker.

## Stack

| Layer | Technology |
|-------|------------|
| Framework | Django 5.2 LTS |
| Authentication | django-allauth (email/password) |
| Styling | Tailwind CSS v4 (standalone CLI) |
| Database | PostgreSQL 17 |
| Containers | Docker + Docker Compose |

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (includes Docker Compose)

### 1. Start Development

```bash
./start-local-dev.sh
```

That's it. The script handles everything:
- Starts PostgreSQL in Docker
- Installs Python dependencies
- Downloads Tailwind CSS CLI
- Runs Django migrations
- Starts the dev server with CSS watch mode

### 2. Access Points

| Service | URL |
|---------|-----|
| Home | [http://localhost:8000](http://localhost:8000) |
| Sign Up | [http://localhost:8000/accounts/signup/](http://localhost:8000/accounts/signup/) |
| Sign In | [http://localhost:8000/accounts/login/](http://localhost:8000/accounts/login/) |
| Dashboard | [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/) |
| Health Check | [http://localhost:8000/health/](http://localhost:8000/health/) |
| Django Admin | [http://localhost:8000/admin/](http://localhost:8000/admin/) |

### 3. Email Verification

New accounts require email verification. In development, verification emails are printed to the Docker console output. Look for the verification link in the terminal and open it in your browser.

## Project Structure

```
.
├── config/                    # Django configuration
│   ├── settings/
│   │   ├── base.py            # Shared settings
│   │   ├── development.py     # Local dev settings
│   │   └── production.py      # Production settings
│   └── urls.py
├── apps/
│   ├── accounts/              # Custom User model (email-based)
│   ├── core/                  # Health check endpoint
│   └── pages/                 # Page views (home, dashboard)
├── templates/                 # Django templates
│   ├── base.html              # Master layout (nav, messages)
│   ├── pages/                 # Page templates
│   └── allauth/               # Auth page styling (Tailwind)
├── static/
│   └── css/
│       └── input.css          # Tailwind v4 source
├── Dockerfile                 # Production image (multi-stage)
├── docker-compose.yml         # Development environment
├── entrypoint.sh              # Startup script (migrations + gunicorn)
├── start-local-dev.sh         # One-command setup
└── .env.example               # Environment template
```

## Development

### Running Commands

```bash
# Django management commands
docker compose exec web python manage.py <command>

# Create a superuser
docker compose exec web python manage.py createsuperuser

# Make migrations
docker compose exec web python manage.py makemigrations

# Run migrations
docker compose exec web python manage.py migrate
```

### How It Works

- Django renders HTML pages using templates with Tailwind CSS classes
- Tailwind CLI watches for class changes and rebuilds CSS automatically
- django-allauth handles authentication (login, signup, logout, password reset)
- All auth flows use Django sessions — no JWT tokens or external services
- Code changes trigger automatic reload (Python via runserver, CSS via Tailwind watch)

### Authentication Flow

1. User visits `/accounts/signup/` and creates an account
2. Verification email prints to the Docker console (dev) or sends via SMTP (prod)
3. User clicks verification link to activate account
4. User logs in at `/accounts/login/`
5. Django session authenticates subsequent requests
6. `@login_required` protects views like `/dashboard/`

## Production

### Build Production Image

```bash
docker build -t __PROJECT_NAME__ .
```

### Run

```bash
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgres://user:pass@host:5432/dbname \
  -e DJANGO_SETTINGS_MODULE=config.settings.production \
  -e ALLOWED_HOSTS=yourdomain.com \
  -e EMAIL_HOST=smtp.example.com \
  -e EMAIL_HOST_USER=noreply@example.com \
  -e EMAIL_HOST_PASSWORD=your-password \
  __PROJECT_NAME__
```

The production image:
- Builds Tailwind CSS with minification (no runtime Tailwind binary)
- Runs Django behind Gunicorn with worker auto-scaling
- Serves static files via WhiteNoise with compression and cache headers
- Waits for DB and runs migrations with advisory lock on startup
- Includes Docker health check on `/health/`
