# Architecture Decisions

## Why django-allauth instead of Clerk?

Clerk is a JavaScript-first auth provider designed for SPAs. For a pure Django project with server-rendered templates, django-allauth is the standard choice:
- Native Django integration (middleware, template tags, session auth)
- No external service dependency — auth works offline
- Email/password out of the box, social login providers ready to add
- Battle-tested in the Django ecosystem (most popular auth package)
- Free and open source with no usage limits

## Why email-only auth (no username)?

- Most modern apps use email as the primary identifier
- Eliminates username uniqueness conflicts
- Simpler signup flow (one less field)
- `AbstractBaseUser + PermissionsMixin` avoids a dead `username` column
- django-allauth supports this natively with `ACCOUNT_USER_MODEL_USERNAME_FIELD = None`

## Why split settings instead of a single file?

- `base.py` contains all shared configuration
- `development.py` enables DEBUG, uses console email backend
- `production.py` enforces HTTPS, configures SMTP email
- Avoids many `if DEBUG:` conditionals in a single file
- `DJANGO_SETTINGS_MODULE` environment variable controls which is active

## Why Tailwind CSS standalone CLI instead of Node.js?

- No Node.js, npm, or package.json anywhere in the project
- Single binary download (~45MB), no dependency tree
- Tailwind v4 uses `@import "tailwindcss"` — one line of CSS, no config file
- Automatic template scanning works with Django templates out of the box
- Development: watch mode alongside `manage.py runserver`
- Production: build step in Docker multi-stage (separate from Python)
- The binary is cached in a Docker volume for fast restarts

## Why advisory lock for migrations?

When scaling with multiple container replicas, all containers start simultaneously and may try to run migrations concurrently. This can cause:
- Duplicate migration attempts
- Database locking errors
- Race conditions on schema changes

The advisory lock (`pg_advisory_lock(1)`) ensures only one container runs migrations at a time. Others wait until the lock is released.

## Why custom User model from day one?

Django's documentation explicitly states: "If you're starting a new project, it's highly recommended to set up a custom user model, even if the default User model is sufficient for you."

Changing AUTH_USER_MODEL after creating the initial migration is extremely difficult and error-prone. Setting it up from the start is practically free.

## Why WhiteNoise for static files?

- Simple setup (one middleware line)
- Serves compressed files with far-future cache headers
- No need for nginx or CDN for small-to-medium apps
- Can be replaced with CDN later without code changes

## Why single container (no nginx)?

- WhiteNoise handles static file serving efficiently
- Gunicorn serves both pages and static files
- One fewer service to manage, configure, and monitor
- nginx adds complexity without meaningful benefit at this scale
- For high traffic, add a CDN in front — not nginx

## Why no DRF (Django REST Framework)?

- Django's built-in views handle HTML templates
- `JsonResponse` handles the health check endpoint
- Users can add DRF later when they need a JSON API
- Fewer dependencies = less to maintain and upgrade

## Database Connection Strategy

- `CONN_MAX_AGE=600` keeps connections alive for 10 minutes (via dj-database-url)
- Suitable for moderate traffic without external connection pooler
- For high traffic, add PgBouncer between Django and PostgreSQL

## Why function-based views for pages?

- `home()` and `dashboard()` are two-line render functions
- `@login_required` is simpler than `LoginRequiredMixin` for this case
- No reason for class-based views when there's no complex logic
- Easy to evolve: add context data, form handling as needed
