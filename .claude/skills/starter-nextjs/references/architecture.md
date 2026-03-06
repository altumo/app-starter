# Architecture Decisions

## Why a single container instead of separate frontend/backend?

Unlike the Django starter which needs separate Python (backend) and Node.js (frontend) containers, Next.js handles both server-side rendering and API routes in a single Node.js process. This simplifies the architecture:
- One container to build, deploy, and monitor
- No inter-service networking for API calls
- No nginx reverse proxy needed
- Server components can query the database directly

## Why Drizzle ORM instead of Prisma?

- **Type-safe from schema to query** - schema defined in TypeScript, queries return typed results
- **SQL-like query builder** - no abstraction layer to learn, maps directly to SQL concepts
- **Lightweight** - no binary engine to download or manage (unlike Prisma's query engine)
- **Migration control** - generates plain SQL files you can review and edit
- **Zero runtime overhead** - compiles to direct SQL, no query engine process

## Why @clerk/nextjs middleware instead of manual JWT verification?

The Django starter uses PyJWT + JWKS because Django has no native Clerk integration. Next.js has first-class Clerk support via `@clerk/nextjs`:
- `clerkMiddleware()` handles JWT verification, session management, and route protection automatically
- `auth()` in server components and API routes provides typed access to user/session/org data
- `currentUser()` provides full user profile data in server components
- No manual JWKS fetching, JWT parsing, or token caching needed
- Clerk components (`<SignIn>`, `<UserButton>`, `<Show>`) work seamlessly with Next.js

## Why proxy.ts instead of middleware.ts?

Next.js 16 renamed `middleware.ts` to `proxy.ts` to:
- Avoid confusion with Express-style middleware (which runs per-request in the handler chain)
- Make the network boundary role explicit (proxy runs before the request reaches the app)
- The proxy runs on the Node.js runtime (edge runtime is no longer supported for this file)

## Why standalone output for Docker?

`output: "standalone"` in `next.config.ts` creates a self-contained build:
- Copies only necessary `node_modules` (90%+ size reduction)
- Outputs a standalone `server.js` that doesn't need `next start`
- Ideal for Docker containers (smaller images, faster startup)

## Why serverExternalPackages for pg and drizzle-orm?

By default, standalone mode bundles all dependencies into the application. However, the migration script (`src/db/migrate.mjs`) needs to import `pg` and `drizzle-orm` directly as Node.js modules (outside the Next.js bundle). `serverExternalPackages` tells Next.js to keep these packages as-is in `node_modules`, making them available to both the app and the migration script.

## Why pg_advisory_lock for migrations?

Same rationale as the Django starter. When scaling with multiple container replicas, all containers start simultaneously and may try to run migrations concurrently. The advisory lock (`pg_advisory_lock(1)`) ensures only one container runs migrations at a time.

## Why drizzle-kit push for development?

- `drizzle-kit push` syncs the TypeScript schema directly to the database without generating migration files
- Perfect for rapid iteration during development (change schema, restart, tables update)
- No migration file management during early development
- Switch to `drizzle-kit generate` + `migrate()` when ready for production deployments

## Why the global singleton pattern for the database connection?

Next.js hot-reloads modules during development. Without the global pattern, each reload creates a new connection pool, eventually exhausting database connections. The singleton pattern stores the pool on `globalThis` so it persists across hot reloads.

## Database Connection Strategy

- Drizzle's `drizzle()` function creates an internal connection pool when passed a URL string
- The pool is managed automatically (connection reuse, idle timeout)
- For high traffic, add PgBouncer between the app and PostgreSQL
