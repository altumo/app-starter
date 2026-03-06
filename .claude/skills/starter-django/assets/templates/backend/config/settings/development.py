from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# CORS - allow all in development
CORS_ALLOW_ALL_ORIGINS = True

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
