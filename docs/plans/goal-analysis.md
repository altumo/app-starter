# Goal Analysis: Replace Next.js with React (Vite)

## Objective

Remove all Next.js dependencies from the `starter-django` skill and replace with a plain React SPA using Vite as the build tool. Django remains the only backend server. The frontend becomes a pure client-side React application.

## Key Architectural Shifts

### 1. API Proxy Pattern
- **Current**: Next.js `rewrites` in `next.config.ts` proxy `/api/*` to Django — frontend has a server
- **New**: Vite dev server proxy in `vite.config.ts` during development; nginx reverse proxy in production Docker — frontend has NO server, only static files

### 2. Authentication Integration
- **Current**: `@clerk/nextjs` — provides middleware, server components, ClerkProvider
- **New**: `@clerk/clerk-react` — client-only provider, hooks, components. No middleware (route protection via React Router)

### 3. Routing
- **Current**: Next.js App Router (file-based), route groups `(auth)/(dashboard)`, catch-all `[[...sign-in]]`, `Link` from `next/link`
- **New**: React Router v7, explicit route config, `<Link>` from `react-router`, protected route wrapper

### 4. Production Serving
- **Current**: Node.js standalone server (`node server.js`), 3-stage Docker build
- **New**: nginx serving static `dist/` files + proxying `/api` to backend, 2-stage Docker build (build + nginx)

### 5. Environment Variables
- **Current**: `NEXT_PUBLIC_` prefix for client-exposed vars
- **New**: `VITE_` prefix for client-exposed vars

### 6. Clerk Middleware → Client-Side Protection
- **Current**: `clerkMiddleware` in `src/middleware.ts` protects routes server-side
- **New**: `ProtectedRoute` component wrapping React Router routes client-side

## Files Inventory

### Frontend Templates — DELETE
- `frontend/next.config.ts`
- `frontend/src/middleware.ts`
- `frontend/src/app/` (entire directory — replaced by pages/layouts/components)

### Frontend Templates — CREATE NEW
- `frontend/vite.config.ts` — Vite config with dev proxy
- `frontend/index.html` — Vite entry point (required at root)
- `frontend/src/main.tsx` — React entry point
- `frontend/src/App.tsx` — Root component with ClerkProvider + Router
- `frontend/src/index.css` — moved from `src/app/globals.css`
- `frontend/src/pages/Home.tsx`
- `frontend/src/pages/SignIn.tsx`
- `frontend/src/pages/SignUp.tsx`
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/layouts/DashboardLayout.tsx`
- `frontend/src/components/ProtectedRoute.tsx`
- `frontend/nginx.conf` — production nginx config for Docker

### Frontend Templates — REWRITE
- `frontend/package.json` — new deps
- `frontend/tsconfig.json` — Vite-compatible
- `frontend/Dockerfile` — nginx-based
- `frontend/.gitignore` — Vite entries
- `frontend/.env.local.example` — VITE_ prefix
- `frontend/src/lib/api.ts` — update comments
- `frontend/postcss.config.mjs` — keep as-is (Tailwind v4)

### Skill Docs — UPDATE
- `SKILL.md` — all Next.js references → React/Vite
- `references/architecture.md` — update proxy and routing sections
- `assets/templates/README.md` — full rewrite of frontend references

### Root Config Templates — UPDATE
- `docker-compose.yml` — frontend service changes
- `docker-compose.prod.yml` — frontend service changes
- `.env.example` — minor updates
- `.gitignore` — update Node.js section
- `start-local-dev.sh` — update references

### Root Project Files — UPDATE
- `README.md` — replace Next.js references
- `MEMORY.md` — update stack info

### Agent Skills — REMOVE
- `.agents/skills/clerk-nextjs-patterns/` — Next.js-specific, no longer relevant
- `skills-lock.json` — remove `clerk-nextjs-patterns` entry

### Backend — NO CHANGES
- CORS already configured for both dev and prod
- Clerk JWT verification is framework-agnostic
- No Next.js references in backend code

## Non-Goals
- Changing the Django backend architecture
- Changing the Clerk JWT verification approach
- Changing the database or Docker base images
- Adding new features beyond what currently exists
