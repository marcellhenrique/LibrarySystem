from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, LoanViewSet, LoanHistoryViewSet
from .health import api_health_check

# Create router and register viewsets
router = DefaultRouter()
router.register('books', BookViewSet)
router.register('loans', LoanViewSet)
router.register('history', LoanHistoryViewSet)

urlpatterns = [
    # Health check endpoint (no auth required)
    path('health/', api_health_check, name='api_health'),
    
    # Router URLs
    path('', include(router.urls)),
]
