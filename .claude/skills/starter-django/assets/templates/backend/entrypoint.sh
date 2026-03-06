#!/bin/bash
set -e

# Default settings module for production
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.production}"

echo "==> Waiting for database..."
MAX_RETRIES=30
RETRY_COUNT=0
until pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -q 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
        echo "ERROR: Database not available after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "    Waiting for database (attempt $RETRY_COUNT/$MAX_RETRIES)..."
    sleep 2
done
echo "==> Database is ready"

echo "==> Running migrations..."
# Use advisory lock to prevent concurrent migration execution
# Lock ID 1 is arbitrary but consistent across all instances
python -c "
import django, os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT pg_advisory_lock(1)')
    try:
        from django.core.management import call_command
        call_command('migrate', '--no-input')
    finally:
        cursor.execute('SELECT pg_advisory_unlock(1)')
"
echo "==> Migrations complete"

echo "==> Starting gunicorn..."
exec gunicorn config.wsgi:application -c gunicorn.conf.py
