# starter-nextjs

Scaffolds a production-ready full-stack project with **Next.js + Drizzle ORM + PostgreSQL + Clerk + Docker**.

## What You Get

```
myapp/
├── src/
│   ├── app/                   # Next.js 16 App Router
│   │   ├── layout.tsx         # Root layout with ClerkProvider
│   │   ├── page.tsx           # Home page (sign-in/sign-up buttons)
│   │   ├── sign-in/           # Clerk sign-in page
│   │   ├── sign-up/           # Clerk sign-up page
│   │   ├── dashboard/         # Protected dashboard (server component)
│   │   └── api/
│   │       ├── health/        # Health check endpoint
│   │       └── auth/me/       # Current user info
│   ├── db/
│   │   ├── schema.ts          # Drizzle schema (users table)
│   │   └── migrate.mjs        # Production migration script + advisory lock
│   └── lib/
│       └── db.ts              # Database connection (singleton)
├── proxy.ts                   # Clerk middleware (Next.js 16 convention)
├── drizzle.config.ts          # Drizzle Kit configuration
├── next.config.ts             # Standalone output + external packages
├── docker-compose.yml         # Dev: PostgreSQL + Next.js
├── docker-compose.prod.yml    # Prod: standalone build
├── Dockerfile                 # Multi-stage (deps → builder → runner)
├── entrypoint.sh              # DB wait + schema sync/migration
├── start-local-dev.sh         # One-command setup
└── .env.example               # All configuration documented
```

~28 files. Single container architecture. Zero manual setup beyond Clerk keys.

## Install

```bash
npx skills add altumo/app-starter -s starter-nextjs
```

## Usage

```bash
claude
```

```
bootstrap a new project called myapp
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Clerk account](https://dashboard.clerk.com) (free tier)

## Setup

### 1. Get Clerk keys

From [dashboard.clerk.com](https://dashboard.clerk.com):
- **Publishable key** (`pk_test_...`)
- **Secret key** (`sk_test_...`)

### 2. Configure environment

Edit `.env`:
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key
CLERK_SECRET_KEY=sk_test_your_key
```

### 3. Start

```bash
./start-local-dev.sh
```

| Service | URL |
|---------|-----|
| App | http://localhost:3000 |
| Health check | http://localhost:3000/api/health |
| Auth info | http://localhost:3000/api/auth/me |

## Common Tasks

```bash
# Open a shell in the container
docker compose exec app sh

# Generate a migration after schema changes
docker compose exec app npx drizzle-kit generate

# Apply migrations
docker compose exec app npm run db:migrate

# Open Drizzle Studio (database browser)
docker compose exec app npx drizzle-kit studio

# Push schema directly (dev shortcut, no migration files)
docker compose exec app npx drizzle-kit push

# Logs
docker compose logs -f app

# Stop / reset
docker compose down        # stop
docker compose down -v     # stop + wipe database
```

## Database Workflow

The schema lives in `src/db/schema.ts`. Drizzle provides two workflows:

**Development** (auto, no migration files):
1. Edit `src/db/schema.ts`
2. Restart the container — `drizzle-kit push` syncs the schema automatically

**Production** (migration files, committed to git):
1. Edit `src/db/schema.ts`
2. Run `npx drizzle-kit generate` to create SQL migration files in `drizzle/`
3. Commit the migration files
4. On deploy, `entrypoint.sh` runs `migrate.mjs` which applies them with `pg_advisory_lock`

## Architecture

- **Single container**: Next.js handles both frontend (SSR) and API routes (no nginx needed)
- **Auth**: `@clerk/nextjs` v7 middleware via `proxy.ts` (Next.js 16 renamed middleware.ts)
- **ORM**: Drizzle with `node-postgres` driver, type-safe from schema to query
- **Migrations**: Programmatic `migrate()` with `pg_advisory_lock` for replica safety
- **Docker**: Standalone output mode (90%+ smaller images), `serverExternalPackages` for migration deps
- **Connection pooling**: Global singleton pattern prevents pool leaks during hot reload
- **Build-time env**: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` passed as Docker build arg for production

See [references/architecture.md](references/architecture.md) for detailed rationale.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Could not connect to PostgreSQL" | Docker Desktop might still be starting. Wait and retry. |
| Clerk sign-in error | Check `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` in `.env`. Restart: `docker compose restart app` |
| 401 on /api/auth/me | Check `CLERK_SECRET_KEY` in `.env`. Restart: `docker compose restart app` |
| Port conflict | Change `APP_PORT` in `.env`: `APP_PORT=3001` |
| Schema push hangs | If drizzle-kit prompts for confirmation, restart the container. Non-breaking changes auto-apply. |
