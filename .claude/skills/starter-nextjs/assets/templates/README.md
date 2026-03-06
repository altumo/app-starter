# __PROJECT_NAME__

Full-stack application built with Next.js, Drizzle ORM, PostgreSQL, and Clerk.

## Stack

- **App**: [Next.js 16](https://nextjs.org/) (App Router, Server Components, API Routes)
- **ORM**: [Drizzle ORM](https://orm.drizzle.team/) (type-safe PostgreSQL)
- **Auth**: [Clerk](https://clerk.com/) (authentication & user management)
- **CSS**: [Tailwind CSS v4](https://tailwindcss.com/)
- **Database**: [PostgreSQL 17](https://www.postgresql.org/)
- **Runtime**: [Node.js 22 LTS](https://nodejs.org/)
- **Containers**: [Docker](https://www.docker.com/) + Docker Compose

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Clerk account](https://dashboard.clerk.com) (free tier available)

### 1. Set up Clerk

1. Create a new application at [dashboard.clerk.com](https://dashboard.clerk.com)
2. Copy your **Publishable Key** and **Secret Key**

### 2. Configure Environment

```bash
cp .env.example .env
```

Update `.env` with your Clerk keys:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_key_here
```

### 3. Start Development

```bash
./start-local-dev.sh
```

Or manually:

```bash
docker compose up --build
```

### Access Points

| Service       | URL                                    |
|---------------|----------------------------------------|
| App           | http://localhost:3000                   |
| Health Check  | http://localhost:3000/api/health        |
| Auth Info     | http://localhost:3000/api/auth/me       |

## Project Structure

```
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── layout.tsx        # Root layout with ClerkProvider
│   │   ├── page.tsx          # Home page
│   │   ├── globals.css       # Tailwind CSS
│   │   ├── sign-in/          # Clerk sign-in page
│   │   ├── sign-up/          # Clerk sign-up page
│   │   ├── dashboard/        # Protected dashboard
│   │   └── api/              # API routes
│   │       ├── health/       # Health check endpoint
│   │       └── auth/me/      # Current user info
│   ├── db/
│   │   ├── schema.ts         # Drizzle schema (source of truth)
│   │   └── migrate.mjs       # Production migration script
│   └── lib/
│       └── db.ts             # Database connection
├── drizzle/                  # Generated SQL migrations
├── proxy.ts                  # Clerk middleware (Next.js 16)
├── drizzle.config.ts         # Drizzle Kit configuration
├── next.config.ts            # Next.js configuration
├── docker-compose.yml        # Development services
├── docker-compose.prod.yml   # Production services
├── Dockerfile                # Multi-stage build
└── entrypoint.sh             # Container startup script
```

## Development Commands

Run commands inside the container:

```bash
# Open a shell
docker compose exec app sh

# Generate a migration after schema changes
docker compose exec app npx drizzle-kit generate

# Apply migrations
docker compose exec app npm run db:migrate

# Open Drizzle Studio (database browser)
docker compose exec app npx drizzle-kit studio

# Push schema directly (development shortcut)
docker compose exec app npx drizzle-kit push
```

## Database Schema

The schema is defined in `src/db/schema.ts` using Drizzle's TypeScript DSL. To make changes:

1. Edit `src/db/schema.ts`
2. For development: restart the container (auto-pushes schema)
3. For production: run `npx drizzle-kit generate` to create a migration file, then commit it

## Authentication Flow

1. User visits the app and sees sign-in/sign-up buttons
2. Clerk handles authentication (hosted UI or embedded components)
3. `proxy.ts` middleware protects `/dashboard` routes (redirects unauthenticated users)
4. Server components use `currentUser()` for user data
5. API routes use `auth()` for authentication checks
6. The `/api/auth/me` endpoint returns the current user's session info

## Production Deployment

Build and run with the production compose file:

```bash
docker compose -f docker-compose.prod.yml up --build
```

Before deploying to production:

1. Generate migration files: `npx drizzle-kit generate`
2. Commit the `drizzle/` directory
3. Set all environment variables (especially `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` as a build arg)
4. Use strong `POSTGRES_PASSWORD`

The production build uses Next.js standalone output for minimal Docker image size.
