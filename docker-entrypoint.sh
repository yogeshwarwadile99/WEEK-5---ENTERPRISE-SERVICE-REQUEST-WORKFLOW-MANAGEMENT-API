#!/bin/sh
set -e

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "✅ Redis is ready!"

# Apply database migrations
echo "⏳ Applying database migrations..."
alembic upgrade head || echo "⚠️ Migrations skipped"

# Start the application
echo "🚀 Starting application..."
exec "$@"