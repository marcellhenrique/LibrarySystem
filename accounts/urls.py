from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, MemberViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register('users', UserViewSet)
router.register('members', MemberViewSet)

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # JWT token refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
