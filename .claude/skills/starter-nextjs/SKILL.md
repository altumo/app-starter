---
name: starter-nextjs
description: Bootstrap a production-ready full-stack project with Next.js + Drizzle ORM + PostgreSQL + Clerk + Docker. Use when starting a new project or when the user says "bootstrap", "scaffold", "starter", "new project", or "init project" with Next.js. Creates turn-key local development with a single command.
---

# Starter Next.js: Full-Stack Project Bootstrap

## Overview

This skill creates a complete, production-ready full-stack project with:
- **App**: Next.js 16 (App Router) + TypeScript + Tailwind CSS v4
- **ORM**: Drizzle ORM with type-safe schema and migrations
- **Auth**: Clerk (@clerk/nextjs middleware + server-side auth)
- **Database**: PostgreSQL 17 with safe migration handling
- **Containers**: Docker Compose for local dev, production Dockerfiles with standalone output

## When to Use

- "Bootstrap a new Next.js project"
- "Create a new Next.js + Drizzle project"
- "Scaffold a full-stack app with Next.js"
- "Set up a new project with Clerk and Next.js"
- "Init project" or "starter" (when Next.js is the desired stack)
- Any request to create a new project using this stack

## Prerequisites

The host machine needs:
- Docker and Docker Compose
- Git

That's it. Everything else runs in containers.

## Instructions

Follow these steps exactly. Read template files from `assets/templates/` relative to this skill directory and write them to the project root. The skill directory is the directory containing this SKILL.md file.

### Step 1: Determine Project Configuration

Ask the user for (or use defaults):
- **Project name** (default: basename of current directory, e.g. `myproject`)

Use the project name as the database name and package name. Replace `__PROJECT_NAME__` in all templates.

### Step 2: Initialize Git Repository

```bash
# Only if not already a git repo
if [ ! -d .git ]; then
  git init
fi
```

### Step 3: Create the App

1. Read and write all files from `assets/templates/` to the project root
2. Replace `__PROJECT_NAME__` with the actual project name in all files
3. Make `entrypoint.sh` and `start-local-dev.sh` executable with `chmod +x`

After writing all files, the structure should be:
```
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── entrypoint.sh
├── start-local-dev.sh
├── .env.example
├── .gitignore
├── README.md
├── package.json
├── next.config.ts
├── tsconfig.json
├── drizzle.config.ts
├── postcss.config.mjs
├── proxy.ts
├── drizzle/                  # Generated migration SQL files
│   └── (created by drizzle-kit generate)
└── src/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── globals.css
    │   ├── sign-in/
    │   │   └── [[...sign-in]]/
    │   │       └── page.tsx
    │   ├── sign-up/
    │   │   └── [[...sign-up]]/
    │   │       └── page.tsx
    │   ├── dashboard/
    │   │   ├── layout.tsx
    │   │   └── page.tsx
    │   └── api/
    │       ├── health/
    │       │   └── route.ts
    │       └── auth/
    │           └── me/
    │               └── route.ts
    ├── db/
    │   ├── schema.ts
    │   └── migrate.mjs
    └── lib/
        └── db.ts
```

### Step 4: Generate .env File

Create `.env` from `.env.example` with local development defaults:
- Set DATABASE_URL to point to the Docker Postgres
- Leave CLERK keys as placeholders (user must get from Clerk dashboard)

### Step 5: Verify Structure

Run `find . -type f | grep -v node_modules | grep -v .git | head -40` to verify the project structure looks correct.

### Step 6: Print Next Steps

Tell the user:

```
Project bootstrapped successfully!

Next steps:
1. Get your Clerk API keys from https://dashboard.clerk.com
2. Update .env with your NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY
3. Run: ./start-local-dev.sh

The app will be available at:
- App: http://localhost:3000
- Health check: http://localhost:3000/api/health
- Auth info: http://localhost:3000/api/auth/me (requires sign-in)

Database commands (run inside container):
- Generate migration: docker compose exec app npx drizzle-kit generate
- Apply migration:    docker compose exec app npm run db:migrate
- Open Drizzle Studio: docker compose exec app npx drizzle-kit studio
```

## Architecture Notes

Read `references/architecture.md` for detailed architecture decisions if needed.

## Important Details

- **Next.js 16 uses proxy.ts** instead of middleware.ts for the Clerk middleware
- **Never hardcode secrets** - all sensitive values come from environment variables
- **The migrate.mjs uses pg_advisory_lock** to prevent migration race conditions when multiple containers start simultaneously
- **Development uses drizzle-kit push** to sync schema directly (no migration files needed)
- **Production uses drizzle-orm migrate()** with committed SQL migration files from the drizzle/ directory
- **The standalone output** with `serverExternalPackages` ensures pg and drizzle-orm are available at runtime for migrations
- **Global singleton pattern** in db.ts prevents connection pool leaks during hot reload
- **NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY** must be available at Docker build time for production (passed as build arg)
