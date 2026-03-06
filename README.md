# App Starter

Production-ready project starters for Claude Code. Each starter is a [skill](https://code.claude.com/docs/en/skills) that scaffolds a complete full-stack app — auth, database, Docker, and all — with a single prompt.

## Available Starters

| Starter | Stack | What You Get |
|---------|-------|-------------|
| [**starter-django**](skills/starter-django/) | Django + React + Vite + PostgreSQL + Clerk | Python backend, React SPA frontend, two containers |
| [**starter-nextjs**](skills/starter-nextjs/) | Next.js + Drizzle ORM + PostgreSQL + Clerk | Single Next.js app with API routes, one container |

Both starters share the same foundation:
- **Auth** via [Clerk](https://clerk.com) (sign-in, sign-up, user management)
- **PostgreSQL 17** with migration safety (`pg_advisory_lock`)
- **Docker Compose** for one-command local development
- **Tailwind CSS v4** with TypeScript
- **Production Dockerfiles** (multi-stage, optimized)
- **Health check endpoints** with database connectivity verification

## Install

```bash
npx skills add altumo/app-starter -s starter-django
```

or

```bash
npx skills add altumo/app-starter -s starter-nextjs
```

This installs the skill into your project's `.claude/skills/` directory.

## Usage

After installing a skill, open Claude Code and say:

```
bootstrap a new project
```

Claude reads the skill, creates all project files (~25-45 files), and prints setup instructions.

## Quick Start (Full Walkthrough)

### 1. Create a project directory and install the skill

```bash
mkdir myapp && cd myapp
npx skills add altumo/app-starter -s starter-nextjs
```

### 2. Bootstrap with Claude Code

```bash
claude
```

Tell Claude:

```
bootstrap a new project called myapp
```

### 3. Get your Clerk keys

1. Go to [dashboard.clerk.com](https://dashboard.clerk.com) and create an app
2. Copy your **Publishable Key** and **Secret Key**
3. Paste them into the generated `.env` file

### 4. Start development

```bash
./start-local-dev.sh
```

Your app is running. Open http://localhost:3000.

## Choosing a Starter

| | starter-django | starter-nextjs |
|---|---|---|
| **Best for** | Teams that want a Python backend with a separate React frontend | Teams that want a single TypeScript codebase |
| **Backend** | Django 5.2 + DRF + Gunicorn | Next.js 16 API Routes |
| **Frontend** | React 19 (Vite SPA) | Next.js 16 App Router (SSR) |
| **ORM** | Django ORM | Drizzle ORM |
| **Auth integration** | PyJWT + JWKS (manual JWT verification) | @clerk/nextjs v7 (native middleware) |
| **Containers** | 3 services (PostgreSQL + Django + Vite) | 2 services (PostgreSQL + Next.js) |
| **Production proxy** | nginx (serves static build + proxies API) | Next.js standalone (serves everything) |
| **Languages** | Python + TypeScript | TypeScript only |

## Also Included

### team-executor

An orchestration skill that assembles expert AI agents to plan and execute complex tasks. Not a project starter — it's a workflow tool.

```bash
npx skills add altumo/app-starter -s team-executor
```

### Reference Skills

These third-party skills are installed in this repo for development. Install them separately if you want them:

| Skill | Source | Install |
|-------|--------|---------|
| django-expert | vintasoftware/django-ai-plugins | `npx skills add vintasoftware/django-ai-plugins -s django-expert` |
| docker-expert | sickn33/antigravity-awesome-skills | `npx skills add sickn33/antigravity-awesome-skills -s docker-expert` |
| vercel-react-best-practices | vercel-labs/agent-skills | `npx skills add vercel-labs/agent-skills -s vercel-react-best-practices` |
| supabase-postgres-best-practices | supabase/agent-skills | `npx skills add supabase/agent-skills -s supabase-postgres-best-practices` |
