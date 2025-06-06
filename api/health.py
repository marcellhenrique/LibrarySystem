from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_health_check(request):
    """Simple health check endpoint that doesn't require authentication"""
    return Response({
        'status': 'healthy',
        'message': 'Library Management System API is running',
        'timestamp': '2025-06-04T23:52:28Z',
        'endpoints': {
            'admin': '/admin/',
            'swagger': '/swagger/',
            'api_books': '/api/books/',
            'api_loans': '/api/loans/',
            'accounts_login': '/api/accounts/users/login/',
            'accounts_members': '/api/accounts/members/'
        }
    })


@csrf_exempt
def simple_health_check(request):
    """Simple health check that works without DRF"""
    return JsonResponse({
        'status': 'ok',
        'message': 'API is running'
    })
