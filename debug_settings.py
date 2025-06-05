#!/usr/bin/env python3
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def check_django_settings():
    """Check Django settings that might cause 400 errors"""
    print("=" * 60)
    print("DJANGO SETTINGS DIAGNOSIS")
    print("=" * 60)
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
    
    print(f"USE_X_FORWARDED_HOST: {getattr(settings, 'USE_X_FORWARDED_HOST', False)}")
    print(f"USE_X_FORWARDED_PORT: {getattr(settings, 'USE_X_FORWARDED_PORT', False)}")
    
    # Check environment variables
    print("\nEnvironment Variables:")
    env_vars = [
        'RAILWAY_ENVIRONMENT_NAME',
        'RAILWAY_PUBLIC_DOMAIN', 
        'ALLOWED_HOSTS',
        'DEBUG',
        'PORT'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'NOT SET')
        print(f"  {var}: {value}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDED FIXES FOR 400 ERRORS:")
    print("=" * 60)
    
    if '*' not in settings.ALLOWED_HOSTS:
        print("⚠️  ALLOWED_HOSTS might be too restrictive")
        print("   Consider adding your Railway domain explicitly")
    
    if settings.DEBUG:
        print("ℹ️  Running in DEBUG mode")
    else:
        print("ℹ️  Running in production mode")
        if not getattr(settings, 'CSRF_TRUSTED_ORIGINS', None):
            print("⚠️  CSRF_TRUSTED_ORIGINS not set for production")

if __name__ == "__main__":
    try:
        check_django_settings()
    except Exception as e:
        print(f"Error checking settings: {e}")
        import traceback
        traceback.print_exc()
