"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api.health import simple_health_check

# Swagger schema configuration
schema_view = get_schema_view(
   openapi.Info(
      title="Library Management System API",
      default_version='v1',
      description="API for managing library books, members, and loans",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@library.local"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Frontend URLs
    path('', include('frontend.urls')),
    
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/accounts/', include('accounts.urls')),
    path('api/', include('api.urls')),
    
    # Swagger documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Health check
    path('health/', simple_health_check, name='health'),
]
