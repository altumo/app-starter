#!/usr/bin/env bash
set -e

echo "==================================="
echo "  __PROJECT_NAME__ - Local Dev Setup"
echo "==================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
  echo "ERROR: Docker is required but not installed."
  echo "Install Docker: https://docs.docker.com/get-docker/"
  exit 1
fi

# Generate .env if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
  echo ""
  echo "IMPORTANT: Update .env with your Clerk API keys"
  echo "  Get them from: https://dashboard.clerk.com"
  echo ""
fi

echo "Starting services..."
docker compose up --build
