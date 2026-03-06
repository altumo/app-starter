# Architecture Decisions

## Why PyJWT instead of clerk-django?

The `clerk-django` package (v1.0.3) is a young wrapper around `clerk-backend-api`. Using PyJWT + JWKS directly gives us:
- Zero dependency on Clerk's Python SDK release cycle
- Full control over JWT verification logic
- Standard JWKS-based verification (works with any OIDC provider)
- Easier to debug and customize

The `ClerkJWTAuthentication` class in `apps/accounts/authentication.py` handles:
- Fetching public keys from Clerk's JWKS endpoint (with caching)
- Verifying JWT signature, expiration, and authorized parties
- Creating a `ClerkUser` object compatible with DRF's authentication system

## Why split settings instead of a single file?

- `base.py` contains all shared configuration
- `development.py` enables DEBUG, allows all CORS origins, uses console email
- `production.py` enforces HTTPS, specific CORS origins, security headers
- Avoids many `if DEBUG:` conditionals in a single file
- `DJANGO_SETTINGS_MODULE` environment variable controls which is active

## Why proxy instead of CORS for development?

- No CORS preflight requests (faster API calls)
- No browser CORS errors to debug
- The proxy is transparent - frontend code just calls `/api/*`
- In development, Vite's built-in dev server proxy forwards `/api/*` to Django
- In production, nginx proxies `/api/*` to Django and serves the static frontend bundle

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

## Database Connection Strategy

- `CONN_MAX_AGE=600` keeps connections alive for 10 minutes (via dj-database-url)
- Suitable for moderate traffic without external connection pooler
- For high traffic, add PgBouncer between Django and PostgreSQL
