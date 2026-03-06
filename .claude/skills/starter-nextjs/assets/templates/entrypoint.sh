#!/bin/bash
set -e

# Parse DB host and port from DATABASE_URL
DB_HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+).*|\1|')
DB_PORT=$(echo "$DATABASE_URL" | sed -E 's|.*:([0-9]+)/.*|\1|')
DB_PORT=${DB_PORT:-5432}

# Wait for PostgreSQL
echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
RETRIES=30
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -q 2>/dev/null || [ $RETRIES -eq 0 ]; do
  echo "  Retrying... ($RETRIES attempts left)"
  RETRIES=$((RETRIES - 1))
  sleep 1
done

if [ $RETRIES -eq 0 ]; then
  echo "ERROR: Could not connect to PostgreSQL"
  exit 1
fi
echo "PostgreSQL is ready"

# Run database migrations
if [ "$NODE_ENV" = "production" ]; then
  echo "Running database migrations..."
  node src/db/migrate.mjs
else
  echo "Syncing database schema..."
  npx drizzle-kit push --force 2>&1 || true
fi

# Start the application
if [ "$NODE_ENV" = "production" ]; then
  echo "Starting production server..."
  exec node server.js
else
  echo "Starting development server..."
  exec npm run dev -- --hostname 0.0.0.0
fi
