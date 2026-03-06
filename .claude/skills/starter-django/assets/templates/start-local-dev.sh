#!/bin/bash
set -e

echo "========================================="
echo "  __PROJECT_NAME__ - Local Development"
echo "========================================="
echo ""

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check docker compose is available
if ! docker compose version > /dev/null 2>&1; then
    echo "ERROR: docker compose is not available. Please install Docker Compose v2."
    exit 1
fi

# Create .env from .env.example if it doesn't exist
if [ ! -f .env ]; then
    echo "==> Creating .env from .env.example..."
    cp .env.example .env

    # Generate a random SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || openssl rand -base64 50 | tr -d '\n')
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|SECRET_KEY=REPLACE_ME_WITH_RANDOM_SECRET|SECRET_KEY=$SECRET_KEY|" .env
    else
        sed -i "s|SECRET_KEY=REPLACE_ME_WITH_RANDOM_SECRET|SECRET_KEY=$SECRET_KEY|" .env
    fi

    echo "    Generated random SECRET_KEY"
    echo ""
    echo "    IMPORTANT: Update .env with your Clerk API keys!"
    echo "    Get them from: https://dashboard.clerk.com > API Keys"
    echo ""
fi

# Create frontend/.env.local from example if it doesn't exist
if [ ! -f frontend/.env.local ]; then
    echo "==> Creating frontend/.env.local from example..."
    cp frontend/.env.local.example frontend/.env.local
    echo ""
    echo "    IMPORTANT: Update frontend/.env.local with your Clerk keys!"
    echo ""
fi

echo "==> Starting services with Docker Compose..."
echo ""
echo "    This may take a few minutes on first run (building images, installing deps)."
echo ""

docker compose up --build

echo ""
echo "Services stopped."
