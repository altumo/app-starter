# Senior Django Architect Analysis: Pure Django Refactor

Analysis date: 2026-03-06

---

## 1. Project Structure

The current templates live under `assets/templates/backend/`. The new structure eliminates the `backend/` subdirectory entirely. The scaffolded project will have `manage.py` at root.

### Current template path (skill repo)

```
skills/starter-django/assets/templates/backend/  -->  skills/starter-django/assets/templates/
```

The skill's template directory itself changes from `assets/templates/backend/` to `assets/templates/`. There is no more `backend/` wrapper.

### New file tree (what gets scaffolded)

```
__PROJECT_NAME__/
    manage.py
    requirements.txt
    Dockerfile
    entrypoint.sh
    gunicorn.conf.py
    .env.example
    .gitignore
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
                entrance.html
                manage.html
            elements/
                button.html
                field.html
                fields.html
                form.html
                alert.html
                h1.html
                h2.html
                hr.html
                p.html
                panel.html
    static/
        css/
            input.css
    staticfiles/           (gitignored, collectstatic output)
```

### Files to DELETE (relative to current `backend/`)

- `apps/accounts/authentication.py` (Clerk JWT auth — entire file)
- `apps/accounts/serializers.py` (DRF serializer — entire file)
- `apps/accounts/views.py` (DRF MeView — entire file)
- `apps/accounts/urls.py` (API auth URLs — entire file)
- `apps/core/urls.py` (will be inlined into config/urls.py or removed)

### Files to CREATE

- `apps/pages/__init__.py`
- `apps/pages/views.py`
- `apps/pages/apps.py`
- `templates/base.html`
- `templates/pages/home.html`
- `templates/pages/dashboard.html`
- `templates/allauth/layouts/base.html`
- `templates/allauth/layouts/entrance.html`
- `templates/allauth/layouts/manage.html`
- `templates/allauth/elements/button.html`
- `templates/allauth/elements/field.html`
- `templates/allauth/elements/fields.html`
- `templates/allauth/elements/form.html`
- `templates/allauth/elements/alert.html`
- `templates/allauth/elements/h1.html`
- `templates/allauth/elements/h2.html`
- `templates/allauth/elements/hr.html`
- `templates/allauth/elements/p.html`
- `templates/allauth/elements/panel.html`
- `static/css/input.css`

### Files to MODIFY

- `config/settings/base.py` (major rewrite)
- `config/settings/development.py` (remove CORS)
- `config/settings/production.py` (remove CORS)
- `config/urls.py` (new URL scheme)
- `apps/accounts/models.py` (remove clerk_id, switch to AbstractBaseUser)
- `apps/accounts/managers.py` (remove Clerk method, simplify)
- `apps/accounts/admin.py` (remove Clerk fields)
- `apps/core/views.py` (rewrite health check as plain Django view)
- `requirements.txt` (swap dependencies)
- `Dockerfile` (update health check URL, add Tailwind build step)
- `entrypoint.sh` (no changes needed, already correct)
- `gunicorn.conf.py` (no changes needed)

### Files UNCHANGED

- `manage.py`
- `config/wsgi.py`
- `config/asgi.py`
- `entrypoint.sh`
- `gunicorn.conf.py`
- `apps/accounts/apps.py`
- `apps/core/apps.py`

---

## 2. Settings — base.py

### Exact file contents

```python
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "allauth",
    "allauth.account",
    # Local apps
    "apps.accounts",
    "apps.core",
    "apps.pages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # allauth
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default="postgres://postgres:postgres@localhost:5432/__PROJECT_NAME__",
        conn_max_age=600,
    )
}

# Custom user model
AUTH_USER_MODEL = "accounts.User"

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === django-allauth configuration ===

# Login via email only (no username)
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"

# Email verification
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3

# Security
ACCOUNT_PREVENT_ENUMERATION = True
ACCOUNT_EMAIL_NOTIFICATIONS = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False

# Redirects
LOGIN_REDIRECT_URL = "/dashboard/"
ACCOUNT_SIGNUP_REDIRECT_URL = "/dashboard/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
```

### Change summary for base.py

**Removed:**
- `"rest_framework"` from INSTALLED_APPS
- `"corsheaders"` from INSTALLED_APPS
- `"corsheaders.middleware.CorsMiddleware"` from MIDDLEWARE
- Entire `REST_FRAMEWORK` dict
- Entire Clerk configuration block (`CLERK_JWKS_URL`, `CLERK_AUTHORIZED_PARTIES`)

**Added:**
- `"allauth"` to INSTALLED_APPS
- `"allauth.account"` to INSTALLED_APPS
- `"apps.pages"` to INSTALLED_APPS
- `"allauth.account.middleware.AccountMiddleware"` to MIDDLEWARE (after XFrameOptionsMiddleware)
- `AUTHENTICATION_BACKENDS` list with ModelBackend + allauth backend
- `TEMPLATES[0]["DIRS"]` set to `[BASE_DIR / "templates"]` (was empty `[]`)
- `STATICFILES_DIRS = [BASE_DIR / "static"]` (new, for project-level static files)
- All `ACCOUNT_*` settings for email-based auth
- `LOGIN_REDIRECT_URL`, `ACCOUNT_SIGNUP_REDIRECT_URL`, `ACCOUNT_LOGOUT_REDIRECT_URL`

**Kept unchanged:**
- Split settings pattern (base/dev/prod)
- WhiteNoise in middleware and STORAGES
- `dj_database_url` database config
- `AUTH_USER_MODEL = "accounts.User"`
- Password validators (with min_length 10)
- LOGGING config
- `python-decouple` for SECRET_KEY and ALLOWED_HOSTS

---

## 3. Settings — development.py

### Exact file contents

```python
from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Email - console backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable HTTPS requirements in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Django Debug Toolbar (uncomment if installed)
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
# INTERNAL_IPS = ["127.0.0.1", "172.0.0.0/8"]
```

### Change summary for development.py

**Removed:**
- `CORS_ALLOW_ALL_ORIGINS = True`

**Kept unchanged:**
- Everything else. The console email backend was already present and is exactly what allauth needs in dev (verification emails print to terminal).

---

## 4. Settings — production.py

### Exact file contents

```python
from decouple import config  # noqa: F811

from .base import *  # noqa: F401,F403

DEBUG = False

# HTTPS settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Email - configure SMTP for production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@example.com")
```

### Change summary for production.py

**Removed:**
- `CORS_ALLOW_ALL_ORIGINS = False`
- Entire `CORS_ALLOWED_ORIGINS` list and its config() call

**Added:**
- `EMAIL_BACKEND` SMTP configuration with decouple-based env vars. This is essential — allauth sends verification emails in production, so SMTP must be configured. All values pull from environment variables with sane defaults so the app doesn't crash if they're missing (it just won't send email).

---

## 5. URL Configuration — urls.py

### Exact file contents

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

### Change summary for urls.py

**Removed:**
- `path("api/", include("apps.core.urls"))` — no more DRF API namespace
- `path("api/auth/", include("apps.accounts.urls"))` — no more Clerk auth endpoints

**Added:**
- `path("accounts/", include("allauth.urls"))` — allauth provides login, signup, logout, password reset, email management, all under `/accounts/`
- `path("health/", health_check, name="health")` — health check moves from `/api/health/` to `/health/` (update Dockerfile HEALTHCHECK accordingly)
- `path("dashboard/", dashboard, name="dashboard")` — protected page view
- `path("", home, name="home")` — public home page

**Design rationale:**
- Page views are simple function-based views imported directly into urls.py. No need for a separate `apps/pages/urls.py` with `include()` for just two routes. This is the Django way — keep it simple until complexity demands otherwise.
- The health check is a plain function view, not a DRF APIView. Imported directly.
- allauth's `include("allauth.urls")` provides all auth-related URLs. No custom auth URLs needed.

---

## 6. User Model

### Decision: AbstractBaseUser + PermissionsMixin (not AbstractUser)

The current model uses `AbstractUser` which inherits a `username` field. Since we're doing email-only auth with no username, we should use `AbstractBaseUser + PermissionsMixin` to avoid carrying a dead `username` column in the database. This is cleaner and aligns with the allauth research document's recommendation.

The alternative — keeping `AbstractUser` and just ignoring the `username` field — works but is sloppy. It leaves a NOT NULL column that either needs a default or needs to be populated with junk data. The allauth docs show `AbstractBaseUser + PermissionsMixin` for email-only setups, and that's the right call.

### models.py — Exact file contents

```python
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with email as the unique identifier."""

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email
```

### Change summary for models.py

**Removed:**
- `AbstractUser` base class (replaced with `AbstractBaseUser, PermissionsMixin`)
- `clerk_id` field entirely
- `REQUIRED_FIELDS = ["username"]` (changed to `[]`)
- Import of `CustomUserManager` (renamed to `UserManager`)

**Added/Changed:**
- `AbstractBaseUser, PermissionsMixin` as base classes
- Explicit `is_active`, `is_staff`, `date_joined` fields (these were inherited from `AbstractUser` before; with `AbstractBaseUser` they must be declared)
- `REQUIRED_FIELDS = []` — email is already required as `USERNAME_FIELD`, nothing else needed
- `objects = UserManager()` — simplified name

### managers.py — Exact file contents

```python
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Manager for custom User model with email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
```

### Change summary for managers.py

**Removed:**
- `CustomUserManager` class (renamed to `UserManager`)
- `get_or_create_from_clerk()` method entirely
- Import of `django.contrib.auth.models.UserManager` (changed to `BaseUserManager`)
- All `username` parameters from `create_user` and `create_superuser`

**Changed:**
- Base class from `UserManager` (Django's) to `BaseUserManager`. This is required because Django's `UserManager` expects a `username` field. `BaseUserManager` is the correct base when you don't have a username.
- `create_user` takes `email` as first positional arg (not `username, email`)
- `create_superuser` validates `is_staff` and `is_superuser` flags
- Class renamed from `CustomUserManager` to `UserManager` (the "Custom" prefix adds nothing)

---

## 7. Views

### apps/pages/__init__.py — Exact file contents

```python
```

(Empty file.)

### apps/pages/apps.py — Exact file contents

```python
from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"
    verbose_name = "Pages"
```

### apps/pages/views.py — Exact file contents

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

### Design rationale for pages views

- Function-based views, not class-based. For pages that just render a template, FBVs are simpler and more readable. No reason to reach for `TemplateView` or `LoginRequiredMixin` when `@login_required` and `render()` do the job in two lines.
- `@login_required` uses Django's built-in decorator, which redirects to `settings.LOGIN_URL` (defaults to `/accounts/login/`, which is exactly where allauth puts the login page). No configuration needed.
- No context data yet. When the project grows, context can be added trivially.

### apps/core/views.py — Exact file contents (rewritten)

```python
import json

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

### Change summary for core/views.py

**Removed:**
- All DRF imports (`APIView`, `Response`, `AllowAny`)
- `HealthCheckView` class

**Replaced with:**
- Plain Django function view using `JsonResponse`
- No authentication needed — `JsonResponse` doesn't go through any auth middleware by default, and the URL isn't behind `login_required`
- Same logic: check database with `SELECT 1`, return JSON with status

### Files to DELETE from apps/core/

- `apps/core/urls.py` — the health check is now wired directly in `config/urls.py`. No need for a separate URL conf for a single route.

### Files to DELETE from apps/accounts/

- `apps/accounts/authentication.py` — Clerk JWT authentication, entirely replaced by allauth session auth
- `apps/accounts/serializers.py` — DRF serializer, no longer needed
- `apps/accounts/views.py` — DRF MeView, no longer needed
- `apps/accounts/urls.py` — API auth URLs, no longer needed

---

## 8. requirements.txt

### Exact file contents

```
Django>=5.2,<5.3
django-allauth>=65.14,<66
dj-database-url>=2.3,<3
gunicorn>=23,<24
whitenoise>=6.8,<7
psycopg[binary]>=3.2,<4
python-decouple>=3.8,<4
```

### Change summary for requirements.txt

**Removed:**
- `djangorestframework>=3.15,<4` — no more DRF
- `django-cors-headers>=4.6,<5` — no more CORS (single-origin app)
- `PyJWT[crypto]>=2.11,<3` — no more Clerk JWT verification

**Added:**
- `django-allauth>=65.14,<66` — pinned to 65.x line which supports Django 5.2 and has the new-style `ACCOUNT_LOGIN_METHODS` / `ACCOUNT_SIGNUP_FIELDS` settings

**Kept unchanged:**
- `Django>=5.2,<5.3`
- `dj-database-url>=2.3,<3`
- `gunicorn>=23,<24`
- `whitenoise>=6.8,<7`
- `psycopg[binary]>=3.2,<4`
- `python-decouple>=3.8,<4`

---

## 9. Admin

### apps/accounts/admin.py — Exact file contents

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model (email-based, no username)."""

    list_display = ("email", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email",)
    ordering = ("email",)

    # Override fieldsets because the default expects username
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Override add_fieldsets for the "add user" form
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login")
```

### Change summary for admin.py

**Removed:**
- `"username"` from `list_display`
- `"clerk_id"` from `list_display` and `search_fields`
- The `("Clerk", {"fields": ("clerk_id",)})` fieldset
- `BaseUserAdmin.fieldsets +` pattern (replaced with fully custom fieldsets)

**Added/Changed:**
- `"date_joined"` added to `list_display`
- Custom `fieldsets` that don't include `username` (Django's default `UserAdmin.fieldsets` has `username` as the first field, which would break with our model)
- Custom `add_fieldsets` for the "add user" form — collects email + password only
- `readonly_fields = ("date_joined", "last_login")` — these are auto-set and shouldn't be editable

**Why override fieldsets entirely:** Django's `BaseUserAdmin.fieldsets` hardcodes `"username"` in the first fieldset. Since our model has no `username` field, we must replace the fieldsets completely or the admin will throw a `FieldError`. This is the standard pattern for email-only User models with Django admin.

---

## 10. Dockerfile Updates

Two changes needed in the Dockerfile.

### Change 1: Health check URL

The health endpoint moves from `/api/health/` to `/health/`.

**Current line 48:**
```dockerfile
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health/')" || exit 1
```

**New line 48:**
```dockerfile
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1
```

### Change 2: Tailwind CSS build step (future consideration)

The goal analysis mentions Tailwind CSS v4 via standalone CLI. This requires a build step in the Dockerfile to compile `static/css/input.css` into `static/css/output.css` before `collectstatic`. This is a separate concern from the Django refactor and should be handled in the Tailwind integration task. The Dockerfile is otherwise unchanged.

---

## 11. Files That Need __init__.py

The following directories need empty `__init__.py` files (the current templates don't include them but they're required for Python package imports):

- `config/__init__.py`
- `config/settings/__init__.py`
- `apps/__init__.py`
- `apps/accounts/__init__.py`
- `apps/core/__init__.py`
- `apps/pages/__init__.py`

These are likely generated by the skill's scaffolding script already. Verify that the skill's `SKILL.md` or generation logic creates them.

---

## 12. .env.example Updates

### Exact file contents

```bash
# Django
SECRET_KEY=change-me-to-a-random-secret-key
DJANGO_SETTINGS_MODULE=config.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://postgres:postgres@db:5432/__PROJECT_NAME__
DB_HOST=db
DB_PORT=5432

# Email (production only)
# EMAIL_HOST=smtp.example.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=noreply@example.com
# EMAIL_HOST_PASSWORD=your-password
# DEFAULT_FROM_EMAIL=noreply@example.com
```

**Removed:** All Clerk env vars (`CLERK_JWKS_URL`, `CLERK_AUTHORIZED_PARTIES`, `CLERK_PUBLISHABLE_KEY`, etc.), all CORS vars, all frontend-specific vars.

**Added:** Email SMTP vars (commented out, for production use).

---

## 13. Summary of Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| `AbstractBaseUser + PermissionsMixin` over `AbstractUser` | No dead `username` column. Clean schema. Matches allauth email-only docs. |
| No `django.contrib.sites` or `SITE_ID` | Not needed for account-only allauth (no social providers). Can be added later. |
| Function-based views for pages | Two-line views don't need class hierarchies. KISS. |
| Health check as plain function | `JsonResponse` does the same thing as DRF `Response` for a JSON endpoint. No reason to keep DRF for one view. |
| Override allauth layouts+elements (not individual page templates) | Style once, apply everywhere. The layered template system means you customize `allauth/elements/button.html` and every allauth page gets styled buttons. |
| `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` | Security best practice. Users must verify email before they can log in. Console backend in dev makes this painless. |
| No `apps/accounts/urls.py` | The accounts app now has no views of its own. It's just a model + admin. allauth provides all the auth URLs. |
| No `apps/core/urls.py` | One health check route doesn't justify a separate URL conf. Wire it directly in `config/urls.py`. |
| Pin allauth to `>=65.14,<66` | Ensures new-style settings (`ACCOUNT_LOGIN_METHODS`, `ACCOUNT_SIGNUP_FIELDS`) are available. The 65.x line has Django 5.2 support. |

---

## 14. Migration Considerations

Since this is a skill that scaffolds **new** projects (not migrating existing ones), there are no migration concerns. The first `manage.py migrate` will create the schema from scratch using the new `AbstractBaseUser`-based model. The `users` table will have: `id`, `password`, `last_login`, `is_superuser`, `email`, `is_active`, `is_staff`, `date_joined`, plus the allauth-managed `account_emailaddress` and `account_emailconfirmation` tables.

---

## 15. What This Analysis Does NOT Cover

These are explicitly out of scope for this analysis but noted for completeness:

1. **Tailwind CSS integration** — The `static/css/input.css`, standalone CLI setup, watch script for dev, and build step for Docker. Separate task.
2. **Template HTML contents** — The actual markup for `base.html`, `home.html`, `dashboard.html`, and allauth element overrides. Depends on Tailwind being set up first.
3. **docker-compose.yml changes** — Removing the frontend service, simplifying to `db` + `web`. Straightforward but separate task.
4. **Documentation updates** — `SKILL.md`, `README.md`, `references/architecture.md`. Separate task.
5. **The skill scaffolding script** — Whatever generates the project from these templates. Needs updating to match new structure. Separate task.
