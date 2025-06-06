#!/bin/bash

# Quick Railway deployment test script
echo "Railway Deployment Test"
echo "======================="

# Test if we can reach the basic endpoints
echo "Testing basic connectivity..."

# Check if Railway environment variables are set
echo "Environment check:"
echo "RAILWAY_ENVIRONMENT_NAME: ${RAILWAY_ENVIRONMENT_NAME:-'NOT SET'}"
echo "RAILWAY_PUBLIC_DOMAIN: ${RAILWAY_PUBLIC_DOMAIN:-'NOT SET'}"
echo "PORT: ${PORT:-'NOT SET'}"

# Show Django settings
echo "Django settings check:"
python -c "
import os, sys
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'RAILWAY_ENVIRONMENT: {getattr(settings, \"RAILWAY_ENVIRONMENT\", \"NOT SET\")}')
" 2>/dev/null || echo "Could not load Django settings"

echo "Deployment test complete."
