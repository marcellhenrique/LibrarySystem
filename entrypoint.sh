#!/bin/bash

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
max_attempts=30
counter=0

# Debug: Show environment variables
echo "Environment variables:"
echo "DATABASE_URL: ${DATABASE_URL:-'not set'}"
echo "PGHOST: ${PGHOST:-'not set'}"
echo "PGPORT: ${PGPORT:-'not set'}"
echo "PGUSER: ${PGUSER:-'not set'}"
echo "PGDATABASE: ${PGDATABASE:-'not set'}"

# Check if we're on Railway and have DATABASE_URL
if [ -n "$DATABASE_URL" ]; then
    echo "Found DATABASE_URL, extracting connection details..."
    echo "DATABASE_URL format: $DATABASE_URL"
    
    # Extract host, port, and user from DATABASE_URL
    # DATABASE_URL format: postgres://user:password@host:port/database
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
    
    echo "Extracted - Host: $DB_HOST, Port: $DB_PORT, User: $DB_USER"
elif [ -n "$PGHOST" ]; then
    echo "Using individual PostgreSQL environment variables..."
    DB_HOST=${PGHOST}
    DB_PORT=${PGPORT:-5432}
    DB_USER=${PGUSER:-postgres}
else
    echo "No database connection info found. Skipping database check..."
    echo "This might be normal if the database service isn't ready yet."
    # Skip database check and proceed with application startup
    DB_HOST=""
    DB_PORT=""
    DB_USER=""
fi

# Only check database connection if we have connection details
if [ -n "$DB_HOST" ] && [ -n "$DB_USER" ]; then
    echo "Checking PostgreSQL connection at $DB_HOST:$DB_PORT as user $DB_USER"
    
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" || [ $counter -eq $max_attempts ]; do
      echo "Waiting for PostgreSQL ($((counter + 1))/$max_attempts)..."
      counter=$((counter + 1))
      sleep 2
    done
    
    if [ $counter -eq $max_attempts ]; then
      echo "Failed to connect to PostgreSQL after $max_attempts attempts"
      echo "Proceeding anyway - Django will handle database connection errors"
    else
          echo "PostgreSQL is ready!"
    fi
else
    echo "Skipping PostgreSQL connection check - no connection details available"
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2
