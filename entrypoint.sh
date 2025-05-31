#!/bin/bash

# Wait for postgres
echo "Waiting for PostgreSQL..."
max_attempts=30
counter=0

until pg_isready -h db -p 5432 -U $POSTGRES_USER || [ $counter -eq $max_attempts ]; do
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
gunicorn config.wsgi:application --bind 0.0.0.0:8000
