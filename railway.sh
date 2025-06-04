#!/bin/bash

# Railway-specific entrypoint script
# This script is more tolerant of Railway's deployment timing

echo "Starting Railway deployment..."

# Show environment for debugging
echo "PORT: ${PORT:-'not set'}"
echo "DATABASE_URL: ${DATABASE_URL:0:50}..." # Show first 50 chars only for security

# Apply database migrations with retry logic
echo "Applying database migrations..."
max_retries=5
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    echo "Migration attempt $((retry_count + 1))/$max_retries"
    
    if python manage.py migrate --noinput; then
        echo "Migrations successful!"
        break
    else
        echo "Migration failed, retrying in 10 seconds..."
        retry_count=$((retry_count + 1))
        sleep 10
    fi
done

if [ $retry_count -eq $max_retries ]; then
    echo "Migrations failed after $max_retries attempts. Starting server anyway..."
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static file collection failed, continuing..."

# Start server
echo "Starting server on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level info
