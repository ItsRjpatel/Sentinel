#!/bin/bash
set -e

# ============================================================
# Azure App Service Startup Script for Sentinel Backend
# ============================================================
# This script runs Alembic migrations and then starts the
# gunicorn ASGI server with UvicornWorker.
#
# Alembic safety: All existing migrations are additive
# (CREATE TABLE, ADD COLUMN). Running 'upgrade head' is safe
# and will be a no-op if the schema is already current.
# The database is NEVER reset, truncated, or destroyed.
# ============================================================

cd /app

echo "Running Alembic database migrations..."
python -m alembic upgrade head
echo "Migrations complete."

echo "Starting Sentinel Backend..."
exec gunicorn \
  --bind=0.0.0.0:${PORT:-8000} \
  --worker-class=uvicorn.workers.UvicornWorker \
  --timeout=120 \
  --workers=2 \
  --access-logfile=- \
  --error-logfile=- \
  app.main:app
