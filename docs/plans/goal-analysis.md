# Goal Analysis: Django + Next.js + Postgres + Clerk + Docker Bootstrap Skill

## Objective

Build a Claude Code skill that bootstraps a production-ready full-stack project using Django (backend API) + Next.js (frontend) + PostgreSQL (database) + Clerk (authentication) + Docker (containerization).

## Distinct Goals

### Goal 1: Git Repository Setup
- Initialize a git repository if not already present
- Set up proper .gitignore for Python, Node.js, and Docker artifacts
- Ensure the project starts clean

### Goal 2: Django Backend Setup
- Create a Django project with best-practices structure
- Custom User model from the start (can't change later)
- Split settings for dev/prod or env-var-driven single settings
- Django REST Framework for API endpoints
- CORS configuration for Next.js frontend
- Health check endpoint
- Gunicorn for production serving
- WhiteNoise for static files
- Proper MIDDLEWARE ordering

### Goal 3: PostgreSQL Database Configuration
- Database connection via DATABASE_URL environment variable
- Connection pooling (CONN_MAX_AGE)
- Migration workflow that works in both dev and production Docker
- Safe migration execution on container startup (race condition handling)

### Goal 4: Clerk Authentication Integration
- Clerk JWT verification in Django (middleware or DRF authentication class)
- Clerk SDK for Python (clerk-backend-api or PyJWT-based verification)
- Clerk provider setup in Next.js frontend
- Clerk middleware in Next.js (middleware.ts)
- Protected API routes pattern: Next.js gets Clerk token -> passes to Django API
- Environment variables for Clerk keys (publishable key, secret key)

### Goal 5: Next.js Frontend Setup
- App Router (modern approach)
- TypeScript by default
- Configured to talk to Django API backend
- API proxy/rewrites for local development
- Clerk provider wrapping the app
- Protected routes with Clerk

### Goal 6: Docker Local Development
- docker-compose.yml with PostgreSQL, Django, Next.js services
- Turn-key: single command to start everything (./start-local-dev.sh)
- Hot-reload for both Django and Next.js in development
- PostgreSQL with health checks
- Automatic database creation and migration on first run
- .env file with sensible defaults for local development
- .env.example with documentation

### Goal 7: Production Docker Configuration
- Multi-stage Dockerfile for Django (small, secure image)
- Multi-stage Dockerfile for Next.js (standalone output)
- Django entrypoint that:
  - Waits for database readiness
  - Runs migrations safely (with lock to prevent race conditions)
  - Collects static files
  - Starts gunicorn
- Production-ready gunicorn configuration
- Health check endpoints in both services

### Goal 8: Developer Experience & Tooling
- .env / .env.example pattern
- start-local-dev.sh script that handles first-time setup
- Requirements management (requirements.txt or pyproject.toml)
- Package.json with useful scripts
- .dockerignore files
- README with getting started instructions

## Inferred Requirements (not explicitly stated but logically necessary)
- CORS headers on Django for Next.js frontend communication
- CSRF exemption for API endpoints (using token auth instead)
- Proper secret key generation for Django
- Node modules and Python venv not committed to git
- Database data persisted via Docker volume
- Environment-specific behavior (DEBUG, ALLOWED_HOSTS, etc.)

## Logical Flow / Dependencies
1. Git init (if needed)
2. Django project scaffold -> settings -> custom user model -> DRF setup
3. Clerk Django integration (authentication backend/middleware)
4. Next.js project scaffold -> Clerk integration -> API client setup
5. Docker compose for local dev (Postgres + Django + Next.js)
6. Production Dockerfiles
7. start-local-dev.sh script
8. .env files and documentation

## Risks & Mitigations
- **Clerk SDK availability for Python**: May need to use PyJWT directly if no official SDK
- **Migration race conditions in production**: Use advisory lock or single-migration container
- **Version pinning**: Pin all dependencies to prevent breaking changes
- **Port conflicts in local dev**: Use non-standard ports or make configurable
- **Database not ready on startup**: Implement wait-for-db pattern
