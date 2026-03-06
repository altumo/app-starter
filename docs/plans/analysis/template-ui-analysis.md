# Template & UI Layer Analysis

## 1. Template Directory Structure

The project is flattening from `backend/` to repo root (Goal 4). Templates live in a project-level `templates/` directory at the repo root, registered via `TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]`. The `static/` directory holds CSS source and compiled output.

```
__PROJECT_NAME__/
  manage.py
  config/
    settings/
      base.py
      development.py
      production.py
  apps/
    accounts/
    pages/               <-- new app for home + dashboard views
  templates/
    base.html            <-- master layout (nav, messages, footer)
    pages/
      home.html          <-- landing page (anonymous + authenticated states)
      dashboard.html     <-- authenticated dashboard
    allauth/
      layouts/
        base.html        <-- allauth layout, extends templates/base.html
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
      input.css          <-- Tailwind v4 source (checked in)
      tailwind.css        <-- Tailwind v4 compiled output (gitignored)
```

Key points:
- `templates/` is at the project root, not inside an app. Registered in settings via `DIRS`.
- `APP_DIRS = True` remains so Django finds admin templates and any app-level templates.
- allauth overrides go in `templates/allauth/` and `templates/account/` (no account-level page overrides needed -- the layout + element approach handles styling).
- The `apps/pages/` app has no `templates/` directory of its own; it uses project-level templates via explicit `template_name` on views.

---

## 2. base.html

```html
{% load static %}
<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}__PROJECT_NAME__{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'css/tailwind.css' %}">
  {% block extra_head %}{% endblock %}
</head>
<body class="h-full bg-gray-50 text-gray-900 antialiased">

  {# ── Navigation ─────────────────────────────────────────── #}
  <nav class="bg-white border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center gap-6">
          <a href="{% url 'home' %}" class="text-xl font-bold text-gray-900">
            __PROJECT_NAME__
          </a>
          {% if user.is_authenticated %}
          <a href="{% url 'dashboard' %}" class="text-sm text-gray-600 hover:text-gray-900 transition">
            Dashboard
          </a>
          {% endif %}
        </div>
        <div class="flex items-center gap-4">
          {% if user.is_authenticated %}
          <span class="text-sm text-gray-600">{{ user.email }}</span>
          <form method="post" action="{% url 'account_logout' %}">
            {% csrf_token %}
            <button type="submit"
                    class="text-sm text-gray-600 hover:text-gray-900 transition">
              Sign Out
            </button>
          </form>
          {% else %}
          <a href="{% url 'account_login' %}"
             class="text-sm text-gray-600 hover:text-gray-900 transition">
            Sign In
          </a>
          <a href="{% url 'account_signup' %}"
             class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition">
            Sign Up
          </a>
          {% endif %}
        </div>
      </div>
    </div>
  </nav>

  {# ── Messages ───────────────────────────────────────────── #}
  {% if messages %}
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
    {% for message in messages %}
    <div class="rounded-lg px-4 py-3 mb-2 text-sm
                {% if message.tags == 'success' %}bg-green-50 text-green-800 border border-green-200
                {% elif message.tags == 'error' %}bg-red-50 text-red-800 border border-red-200
                {% elif message.tags == 'warning' %}bg-yellow-50 text-yellow-800 border border-yellow-200
                {% else %}bg-blue-50 text-blue-800 border border-blue-200{% endif %}"
         role="alert">
      {{ message }}
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {# ── Page Content ───────────────────────────────────────── #}
  {% block content %}{% endblock %}

  {% block extra_js %}{% endblock %}
</body>
</html>
```

Notes:
- The `user` variable is available globally via Django's `auth` context processor (already in settings).
- `messages` comes from the `messages` context processor (already in settings).
- Logout is a POST form with CSRF token -- allauth default (`ACCOUNT_LOGOUT_ON_GET = False`).
- No JavaScript framework loaded. Pure HTML + Tailwind.

---

## 3. Home Page Template

```html
{# templates/pages/home.html #}
{% extends "base.html" %}

{% block title %}__PROJECT_NAME__{% endblock %}

{% block content %}
<main class="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center px-4">
  <h1 class="text-4xl font-bold mb-8 text-gray-900">__PROJECT_NAME__</h1>

  {% if user.is_authenticated %}
  <div class="flex flex-col items-center gap-4">
    <p class="text-gray-600">Welcome back, {{ user.email }}</p>
    <a href="{% url 'dashboard' %}"
       class="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition">
      Go to Dashboard
    </a>
  </div>
  {% else %}
  <div class="flex gap-4">
    <a href="{% url 'account_login' %}"
       class="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition">
      Sign In
    </a>
    <a href="{% url 'account_signup' %}"
       class="inline-flex items-center px-6 py-3 text-base font-medium text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition">
      Sign Up
    </a>
  </div>
  {% endif %}
</main>
{% endblock %}
```

Corresponding view in `apps/pages/views.py`:

```python
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "pages/home.html"
```

---

## 4. Dashboard Template

```html
{# templates/pages/dashboard.html #}
{% extends "base.html" %}

{% block title %}Dashboard - __PROJECT_NAME__{% endblock %}

{% block content %}
<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <h1 class="text-2xl font-bold mb-6 text-gray-900">Dashboard</h1>
  <div class="grid gap-4 md:grid-cols-2">

    {# Welcome Card #}
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <h2 class="text-lg font-semibold mb-2 text-gray-900">Welcome</h2>
      <p class="text-gray-600">Hello, {{ user.email }}!</p>
    </div>

    {# Health Check Card #}
    <div class="bg-white rounded-lg border border-gray-200 p-6">
      <h2 class="text-lg font-semibold mb-2 text-gray-900">System Status</h2>
      <p class="text-gray-600">
        Health:
        <span class="font-medium
                     {% if health_status == 'healthy' %}text-green-600{% else %}text-red-600{% endif %}">
          {{ health_status }}
        </span>
      </p>
    </div>

  </div>
</main>
{% endblock %}
```

Corresponding view in `apps/pages/views.py`:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["health_status"] = "healthy"  # DB connection already proven by serving this page
        return context
```

Notes:
- `LoginRequiredMixin` replaces the React `ProtectedRoute`. Unauthenticated users get redirected to `account_login` automatically (Django's `LOGIN_URL` defaults to `/accounts/login/`, which is the allauth login).
- Health status is computed server-side. Since the view is served by Django with a DB-backed session, the database is already proven reachable. For a more thorough check, the view could ping the DB explicitly, but for a starter template "healthy" is appropriate -- the real health endpoint (`/api/health/`) still exists separately.
- No client-side fetch needed. Server rendering eliminates the loading state the React version required.

---

## 5. Dashboard Layout Strategy

The React version uses `DashboardLayout` as a layout route with `<Outlet />`. In Django templates, this pattern is handled by template inheritance -- `base.html` already contains the nav bar with conditional dashboard links.

There is **no need for a separate dashboard base template**. Here is why:

- The React `DashboardLayout` adds: (1) a nav bar with project name + dashboard link + user button, (2) a `max-w-7xl` content wrapper. Both of these are already in `base.html`.
- The nav bar in `base.html` shows the Dashboard link only when `user.is_authenticated`, which is the exact same conditional the React version enforces via `ProtectedRoute`.
- Each dashboard-area page template applies its own `max-w-7xl mx-auto` wrapper in its `{% block content %}`, matching the React layout's `<main>` wrapper.

If the project later adds multiple dashboard sub-pages (settings, profile, etc.) that need a sidebar or tabs, a `templates/dashboard_base.html` can be introduced that extends `base.html` and adds sidebar markup. For now, the single-level inheritance (`dashboard.html` extends `base.html`) is sufficient and avoids premature abstraction.

---

## 6. allauth Template Overrides

### 6a. `templates/allauth/layouts/base.html`

This is the root layout for all allauth pages. It extends our project's `base.html` so allauth pages inherit the same nav, messages, and styling.

```html
{# templates/allauth/layouts/base.html #}
{% extends "base.html" %}

{% block content %}
<main class="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-12">
  <div class="w-full max-w-md">
    {% block body %}{% endblock %}
  </div>
</main>
{% endblock %}
```

Notes:
- allauth pages render into `{% block body %}`, which we place inside a centered card-like container.
- `min-h-[calc(100vh-4rem)]` accounts for the nav bar height (h-16 = 4rem) so the form is vertically centered in the remaining viewport.
- allauth's `entrance.html` and `manage.html` extend this base by default, so we only need to override this one layout file.

### 6b. `templates/allauth/elements/button.html`

```html
{# templates/allauth/elements/button.html #}
{% load allauth %}
{% if "socialaccount" in tags %}
<button {{ attrs }}
        class="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition">
  {% render_slot slots.default %}
</button>
{% elif "primary" in tags %}
<button {{ attrs }}
        class="inline-flex w-full items-center justify-center rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed">
  {% render_slot slots.default %}
</button>
{% elif "secondary" in tags %}
<button {{ attrs }}
        class="inline-flex w-full items-center justify-center rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed">
  {% render_slot slots.default %}
</button>
{% elif "danger" in tags %}
<button {{ attrs }}
        class="inline-flex w-full items-center justify-center rounded-lg bg-red-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed">
  {% render_slot slots.default %}
</button>
{% elif "link" in tags %}
<button {{ attrs }}
        class="text-sm font-medium text-blue-600 hover:text-blue-500 transition">
  {% render_slot slots.default %}
</button>
{% else %}
<button {{ attrs }}
        class="inline-flex w-full items-center justify-center rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed">
  {% render_slot slots.default %}
</button>
{% endif %}
```

### 6c. `templates/allauth/elements/field.html`

```html
{# templates/allauth/elements/field.html #}
{% load allauth %}
<div class="mb-4">
  {% if field.label %}
  <label for="{{ field.id_for_label }}"
         class="block text-sm font-medium text-gray-700 mb-1">
    {{ field.label }}
  </label>
  {% endif %}
  {% render_slot slots.default %}
  <input {{ attrs }}
         class="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 transition">
  {% for error in field.errors %}
  <p class="mt-1 text-sm text-red-600">{{ error }}</p>
  {% endfor %}
  {% if field.help_text %}
  <p class="mt-1 text-sm text-gray-500">{{ field.help_text }}</p>
  {% endif %}
</div>
```

### 6d. `templates/allauth/elements/form.html`

```html
{# templates/allauth/elements/form.html #}
{% load allauth %}
<form {{ attrs }}>
  {% csrf_token %}
  {% render_slot slots.body %}
  {% if slots.actions %}
  <div class="mt-6 flex flex-col gap-3">
    {% render_slot slots.actions %}
  </div>
  {% endif %}
</form>
```

### 6e. `templates/allauth/elements/h1.html`

```html
{# templates/allauth/elements/h1.html #}
{% load allauth %}
<h1 class="text-2xl font-bold text-gray-900 mb-2">
  {% render_slot slots.default %}
</h1>
```

### 6f. `templates/allauth/elements/h2.html`

```html
{# templates/allauth/elements/h2.html #}
{% load allauth %}
<h2 class="text-lg font-semibold text-gray-900 mb-1">
  {% render_slot slots.default %}
</h2>
```

### 6g. `templates/allauth/elements/hr.html`

```html
{# templates/allauth/elements/hr.html #}
<div class="my-6 flex items-center gap-4">
  <div class="flex-grow border-t border-gray-200"></div>
  <span class="text-sm text-gray-400">or</span>
  <div class="flex-grow border-t border-gray-200"></div>
</div>
```

### 6h. `templates/allauth/elements/alert.html`

```html
{# templates/allauth/elements/alert.html #}
{% load allauth %}
{% if "error" in tags or "danger" in tags %}
<div class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 mb-4 text-sm text-red-800" role="alert">
  {% render_slot slots.default %}
</div>
{% elif "success" in tags %}
<div class="rounded-lg bg-green-50 border border-green-200 px-4 py-3 mb-4 text-sm text-green-800" role="alert">
  {% render_slot slots.default %}
</div>
{% elif "warning" in tags %}
<div class="rounded-lg bg-yellow-50 border border-yellow-200 px-4 py-3 mb-4 text-sm text-yellow-800" role="alert">
  {% render_slot slots.default %}
</div>
{% else %}
<div class="rounded-lg bg-blue-50 border border-blue-200 px-4 py-3 mb-4 text-sm text-blue-800" role="alert">
  {% render_slot slots.default %}
</div>
{% endif %}
```

### 6i. `templates/allauth/elements/panel.html`

```html
{# templates/allauth/elements/panel.html #}
{% load allauth %}
<div class="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
  {% if slots.title %}
  <div class="mb-6">
    {% render_slot slots.title %}
  </div>
  {% endif %}
  {% render_slot slots.body %}
  {% if slots.actions %}
  <div class="mt-6 flex flex-col gap-3">
    {% render_slot slots.actions %}
  </div>
  {% endif %}
</div>
```

### 6j. `templates/allauth/elements/p.html`

```html
{# templates/allauth/elements/p.html #}
{% load allauth %}
<p class="text-sm text-gray-600 mb-4">
  {% render_slot slots.default %}
</p>
```

### Summary of allauth override strategy

Only **layouts** and **elements** are overridden. The actual page templates (`account/login.html`, `account/signup.html`, etc.) are left at allauth defaults. allauth's built-in page templates use the `{% element %}` tags, so overriding the elements applies Tailwind classes globally across all auth pages (login, signup, password reset, email confirmation, etc.) without touching each page individually. This is the correct approach per the allauth docs -- style the building blocks, not the pages.

---

## 7. Tailwind input.css

### Location

```
static/css/input.css
```

This file is checked into git. It is the Tailwind entry point.

### Contents

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

### Why `source("../../")`

The CSS file lives at `static/css/input.css`. The `source("../../")` directive tells Tailwind to scan from the project root (two levels up from `static/css/`). This ensures it finds:
- `templates/**/*.html` -- all Django templates with Tailwind classes
- `apps/**/*.py` -- any Python files with class strings (view context, form widgets)
- `static/**/*.js` -- any future JS files

Tailwind v4 auto-detects files, respects `.gitignore`, and skips binary files. No explicit content paths are needed.

### Build commands

```bash
# Development (watch mode)
tailwindcss -i static/css/input.css -o static/css/tailwind.css --watch

# Production (minified)
tailwindcss -i static/css/input.css -o static/css/tailwind.css --minify
```

### Theme rationale

The `@theme` block defines `primary-*` color tokens using oklch. These are not used in the templates above (which use `blue-*` directly), but they provide a customization point. A developer can switch from blue to any brand color by editing these tokens and replacing `blue-*` with `primary-*` in templates. Including the theme block in the starter demonstrates the v4 pattern without forcing it.

---

## 8. Static Files Setup

### Directory layout

```
static/                      <-- STATICFILES_DIRS entry
  css/
    input.css                <-- Tailwind source (checked in)
    tailwind.css             <-- Tailwind compiled output (gitignored)
  js/                        <-- future JS files (empty for now)
staticfiles/                 <-- STATIC_ROOT (collectstatic output, gitignored)
```

### Settings

```python
# config/settings/base.py

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

### How it works

1. **Development**: `input.css` and `tailwind.css` both live in `static/css/`. Django's dev server serves files from `STATICFILES_DIRS` directly. The Tailwind watch process writes `tailwind.css` into `static/css/`, and the browser loads it via `{% static 'css/tailwind.css' %}`.

2. **Production (Docker build)**: The Dockerfile runs the Tailwind CLI in a build stage to generate `static/css/tailwind.css`. Then `collectstatic` copies everything from `static/` (including the compiled `tailwind.css`) into `staticfiles/`. WhiteNoise serves from `staticfiles/` with compression and cache headers.

3. **collectstatic interaction**: `collectstatic` copies `static/css/tailwind.css` to `staticfiles/css/tailwind.<hash>.css`. WhiteNoise's `CompressedManifestStaticFilesStorage` handles the hash-based cache busting. The `{% static 'css/tailwind.css' %}` tag resolves to the hashed filename automatically.

4. **What gets gitignored**: `static/css/tailwind.css` (generated output) and `staticfiles/` (collectstatic output). Only `static/css/input.css` is committed.

### .gitignore additions

```gitignore
# Tailwind compiled output
static/css/tailwind.css

# Django collectstatic output
staticfiles/
```

### Docker multi-stage build (Tailwind stage)

```dockerfile
# ── Stage 1: Build Tailwind CSS ──────────────────────────────
FROM debian:bookworm-slim AS tailwind-build

ARG TAILWIND_VERSION=4.1.3
ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && ARCH=$(case ${TARGETARCH} in \
         amd64) echo "x64" ;; \
         arm64) echo "arm64" ;; \
         *) echo "x64" ;; \
       esac) \
    && curl -sL -o /usr/local/bin/tailwindcss \
       "https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}/tailwindcss-linux-${ARCH}" \
    && chmod +x /usr/local/bin/tailwindcss \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY templates/ ./templates/
COPY static/css/input.css ./static/css/input.css

RUN tailwindcss -i static/css/input.css -o static/css/tailwind.css --minify

# ── Stage 2: Python ──────────────────────────────────────────
FROM python:3.12-slim-bookworm AS final
# ... Python setup ...
COPY --from=tailwind-build /build/static/css/tailwind.css /app/static/css/tailwind.css
```

The key insight: only `templates/` and `static/css/input.css` are copied into the Tailwind build stage. These are the only files Tailwind needs to scan for classes and produce the output. The Python code in `apps/` could also be copied if views contain Tailwind class strings, but for this starter the classes are exclusively in templates.

### Development workflow

Two terminal processes:

```bash
# Terminal 1: Django dev server
python manage.py runserver

# Terminal 2: Tailwind watch
tailwindcss -i static/css/input.css -o static/css/tailwind.css --watch
```

The `start-local-dev.sh` script (or `docker-compose.yml`) should run both. In Docker Compose, the Tailwind watch can be a command prefix or a separate service. The simplest approach for the dev container:

```yaml
services:
  web:
    command: >
      sh -c "tailwindcss -i static/css/input.css -o static/css/tailwind.css --watch &
             python manage.py runserver 0.0.0.0:8000"
```

This backgrounds the Tailwind watcher and runs Django in the foreground. The watcher rebuilds CSS on template changes; Django's dev server picks up the new `tailwind.css` on the next page reload.
