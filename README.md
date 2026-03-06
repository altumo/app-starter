# App Starter

A toolkit of Claude Code skills that bootstrap production-ready projects for different stacks. Each starter is a self-contained skill that scaffolds a complete project with best-practices defaults, turn-key local development, and production-ready configuration.

## Starters

| Starter | Stack | Status |
|---------|-------|--------|
| [`starter-django`](.claude/skills/starter-django/) | Django + React + Vite + PostgreSQL + Clerk + Docker | Available |

## How It Works

Each starter is a [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code) that lives in `.claude/skills/`. When invoked, Claude reads the skill's templates and generates a complete project scaffold in your working directory.

## Getting Started (starter-django)

### Prerequisites

1. **Docker Desktop** — install from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) and make sure it's running
2. **Claude Code** — `npm install -g @anthropic-ai/claude-code`
3. **Clerk account** — sign up at [dashboard.clerk.com](https://dashboard.clerk.com) (free tier works)

### Step 1: Create your project directory

```bash
mkdir ~/projects/myapp && cd ~/projects/myapp
```

### Step 2: Install the skill

Copy the skill into your project's Claude Code skills directory:

```bash
mkdir -p .claude/skills
cp -r /path/to/app-starter/.claude/skills/starter-django .claude/skills/
```

Or, if this repo is your starting point, just work inside it directly.

### Step 3: Bootstrap with Claude Code

```bash
claude
```

Then tell Claude:

```
bootstrap a new project called myapp
```

Claude will read the skill, create ~45 files (backend, frontend, Docker, config), generate a secret key, and print next steps.

### Step 4: Get your Clerk keys

1. Go to [dashboard.clerk.com](https://dashboard.clerk.com) → create an application
2. Go to **API Keys** and copy:
   - **Publishable key** (`pk_test_...`)
   - **Secret key** (`sk_test_...`)
3. Go to **API Keys → Advanced** and note your **Frontend API URL** — your JWKS URL is:
   ```
   https://<your-frontend-api>.clerk.accounts.dev/.well-known/jwks.json
   ```

### Step 5: Configure environment

Edit `.env` (root):
```bash
CLERK_JWKS_URL=https://your-instance.clerk.accounts.dev/.well-known/jwks.json
```

Edit `frontend/.env.local`:
```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_key
```

### Step 6: Start development

```bash
./start-local-dev.sh
```

First run takes a few minutes (pulling Docker images, installing dependencies). After that:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api/ |
| Health check | http://localhost:8000/api/health/ |
| Django Admin | http://localhost:8000/admin/ |

### Step 7: Verify it works

1. Open http://localhost:3000 — you should see a landing page with Sign In / Sign Up buttons
2. Sign up via Clerk
3. You'll land on the dashboard which shows the backend health status
4. Check http://localhost:8000/api/health/ — should return `{"status": "healthy"}`

## Common Tasks

```bash
# Run Django management commands
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate

# Install a new npm package
docker compose exec frontend npm install <package>

# Install a new Python package
# Add to backend/requirements.txt, then:
docker compose up --build backend

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop everything
docker compose down

# Stop and wipe database
docker compose down -v
```

## Troubleshooting

**"Database not available"** — Docker Desktop might still be starting. Wait a few seconds and retry.

**Clerk sign-in shows an error** — Double-check that `VITE_CLERK_PUBLISHABLE_KEY` in `frontend/.env.local` matches your Clerk dashboard. Restart the frontend container after changing env vars: `docker compose restart frontend`.

**Backend returns 401 on authenticated requests** — Verify `CLERK_JWKS_URL` in `.env` points to your Clerk instance's JWKS endpoint. Restart the backend: `docker compose restart backend`.

**Port already in use** — Edit `.env` to change ports:
```bash
BACKEND_PORT=8001
FRONTEND_PORT=3001
DB_PORT=5433
```

## Bundled Reference Skills

These domain-expert skills enhance Claude's capabilities when working on bootstrapped projects:

- **django-expert** — Django models, views, DRF, migrations, security, production deployment
- **docker-expert** — Multi-stage builds, Compose orchestration, container security
- **vercel-react-best-practices** — React performance optimization
- **supabase-postgres-best-practices** — PostgreSQL performance, indexing, query optimization

## Contributing a Starter

Each starter follows the Claude Code skill format:

```
.claude/skills/{starter-name}/
├── SKILL.md              # Instructions Claude follows to scaffold the project
├── assets/templates/     # All project template files
├── references/           # Architecture decisions, design docs
└── scripts/              # Helper scripts (optional)
```

The `SKILL.md` frontmatter must include `name` and `description` fields. See the [starter-django skill](.claude/skills/starter-django/SKILL.md) as a reference implementation.
