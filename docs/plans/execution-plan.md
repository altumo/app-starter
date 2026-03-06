# Execution Plan: Replace Next.js with React (Vite)

## Overview

Remove all Next.js dependencies from the starter-django skill and replace with a plain React SPA using Vite. The frontend becomes static files served by nginx in production, with Vite's dev proxy replacing Next.js rewrites. Django remains the sole backend.

## Goals

1. Replace all Next.js frontend templates with Vite + React Router + @clerk/clerk-react equivalents
2. Update Docker configuration for static-file serving (nginx) instead of Node.js server
3. Update all documentation and skill instructions to reflect React/Vite stack
4. Remove the `clerk-nextjs-patterns` agent skill (Next.js-specific)
5. Update project memory to reflect new stack

## Architecture

```
project-root/
├── backend/                    # Django project (UNCHANGED)
│   ├── config/settings/
│   ├── apps/
│   ├── Dockerfile
│   └── entrypoint.sh
├── frontend/                   # React SPA (Vite)
│   ├── src/
│   │   ├── main.tsx            # Entry point
│   │   ├── App.tsx             # ClerkProvider + Router
│   │   ├── index.css           # Tailwind
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── SignIn.tsx
│   │   │   ├── SignUp.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── layouts/
│   │   │   └── DashboardLayout.tsx
│   │   ├── components/
│   │   │   └── ProtectedRoute.tsx
│   │   └── lib/
│   │       └── api.ts
│   ├── index.html              # Vite entry
│   ├── vite.config.ts          # Dev proxy + build config
│   ├── tsconfig.json
│   ├── postcss.config.mjs
│   ├── package.json
│   ├── nginx.conf              # Production serving
│   ├── Dockerfile
│   ├── .env.local.example
│   └── .gitignore
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── start-local-dev.sh
└── README.md
```

### Key Decisions

1. **Vite dev proxy** replaces Next.js rewrites — same DX, simpler stack
2. **React Router v7** for client-side routing — explicit routes, protected route wrapper
3. **@clerk/clerk-react** instead of `@clerk/nextjs` — client-only, no server components
4. **nginx** serves static files in production and proxies `/api` to Django backend
5. **No SSR** — pure client-side React SPA

## Execution Steps

### Phase 1: Delete Next.js Frontend Templates

#### Step 1.1: Remove Next.js-specific files
**Objective**: Delete files that have no React/Vite equivalent
**Files to delete**:
- `assets/templates/frontend/next.config.ts`
- `assets/templates/frontend/src/middleware.ts`
- `assets/templates/frontend/src/app/` (entire directory)

### Phase 2: Create New React Frontend Templates

#### Step 2.1: Create vite.config.ts
**Objective**: Vite config with dev proxy to Django
**File**: `assets/templates/frontend/vite.config.ts`

#### Step 2.2: Create index.html
**Objective**: Vite entry point HTML
**File**: `assets/templates/frontend/index.html`

#### Step 2.3: Create main.tsx
**Objective**: React entry point
**File**: `assets/templates/frontend/src/main.tsx`

#### Step 2.4: Create App.tsx
**Objective**: Root component with ClerkProvider + BrowserRouter + Routes
**File**: `assets/templates/frontend/src/App.tsx`

#### Step 2.5: Create index.css
**Objective**: Tailwind import (moved from globals.css)
**File**: `assets/templates/frontend/src/index.css`

#### Step 2.6: Create page components
**Files**:
- `assets/templates/frontend/src/pages/Home.tsx`
- `assets/templates/frontend/src/pages/SignIn.tsx`
- `assets/templates/frontend/src/pages/SignUp.tsx`
- `assets/templates/frontend/src/pages/Dashboard.tsx`

#### Step 2.7: Create DashboardLayout
**File**: `assets/templates/frontend/src/layouts/DashboardLayout.tsx`

#### Step 2.8: Create ProtectedRoute
**Objective**: Client-side route protection (replaces Clerk middleware)
**File**: `assets/templates/frontend/src/components/ProtectedRoute.tsx`

#### Step 2.9: Create nginx.conf
**Objective**: Production nginx config for SPA + API proxy
**File**: `assets/templates/frontend/nginx.conf`

### Phase 3: Rewrite Existing Frontend Templates

#### Step 3.1: Rewrite package.json
**Changes**: Remove next/@clerk/nextjs, add vite/react-router/@clerk/clerk-react

#### Step 3.2: Rewrite tsconfig.json
**Changes**: Remove Next.js plugin, update for Vite

#### Step 3.3: Rewrite Dockerfile
**Changes**: 2-stage build (node build + nginx serve) instead of 3-stage Next.js standalone

#### Step 3.4: Rewrite .gitignore
**Changes**: Remove .next/, add dist/

#### Step 3.5: Rewrite .env.local.example
**Changes**: VITE_ prefix instead of NEXT_PUBLIC_

#### Step 3.6: Update api.ts
**Changes**: Update comments about proxy mechanism

### Phase 4: Update Docker & Root Config Templates

#### Step 4.1: Update docker-compose.yml
**Changes**: Frontend service uses Vite dev server instead of Next.js

#### Step 4.2: Update docker-compose.prod.yml
**Changes**: Frontend builds to nginx instead of Node.js server

#### Step 4.3: Update .env.example
**Changes**: Minor — remove FRONTEND_PORT if not needed, update comments

#### Step 4.4: Update root .gitignore
**Changes**: Update Node.js section (remove .next, add dist)

#### Step 4.5: Update start-local-dev.sh
**Changes**: Update any Next.js references in output/comments

### Phase 5: Update Documentation

#### Step 5.1: Rewrite SKILL.md
**Changes**: All Next.js references → React/Vite, update file tree, update step 4

#### Step 5.2: Update architecture.md
**Changes**: Update proxy section, add Vite/nginx reasoning

#### Step 5.3: Rewrite template README.md
**Changes**: Full update of stack table, project structure, auth flow

#### Step 5.4: Update root README.md
**Changes**: Replace Next.js references with React/Vite

### Phase 6: Clean Up Agent Skills & Memory

#### Step 6.1: Remove clerk-nextjs-patterns
**Action**: Delete `.agents/skills/clerk-nextjs-patterns/` directory

#### Step 6.2: Update skills-lock.json
**Action**: Remove `clerk-nextjs-patterns` entry

#### Step 6.3: Update MEMORY.md
**Action**: Replace Next.js stack info with React/Vite

## Quality Criteria

- No remaining references to "Next.js", "next.config", "@clerk/nextjs", "App Router", "middleware.ts" in the skill
- All frontend templates are valid React/Vite files
- Docker configs work with nginx-based frontend
- Vite dev proxy correctly routes to Django
- Clerk auth still works end-to-end (same JWT flow, different client SDK)
- README and SKILL.md accurately describe the new stack
