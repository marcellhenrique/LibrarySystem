#!/bin/bash

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
max_attempts=30
counter=0

# Railway provides DATABASE_URL, extract connection details from it
if [ -n "$DATABASE_URL" ]; then
    # Extract host, port, and user from DATABASE_URL
    # DATABASE_URL format: postgres://user:password@host:port/database
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
else
    # Fallback to individual environment variables
    DB_HOST=${PGHOST:-localhost}
    DB_PORT=${PGPORT:-5432}
    DB_USER=${PGUSER:-postgres}
fi

# Ensure variables are not empty
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}

echo "Connecting to PostgreSQL at $DB_HOST:$DB_PORT as user $DB_USER"

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" || [ $counter -eq $max_attempts ]; do
  echo "Waiting for PostgreSQL ($((counter + 1))/$max_attempts)..."
  counter=$((counter + 1))
  sleep 2
done

if [ $counter -eq $max_attempts ]; then
  echo "Failed to connect to PostgreSQL after $max_attempts attempts"
  exit 1
fi

echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2
