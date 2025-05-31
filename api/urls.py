from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, LoanViewSet, LoanHistoryViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register('books', BookViewSet)
router.register('loans', LoanViewSet)
router.register('history', LoanHistoryViewSet)

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
]
