from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from django.conf import settings
from .models import User, Member
from .serializers import UserSerializer, LoginSerializer, MemberSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User (staff) operations"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Configure permissions based on action"""
        if self.action in ['login', 'register']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Ensure default values
            serializer.validated_data['is_staff_member'] = False
            serializer.validated_data['is_staff'] = False
            serializer.validated_data['is_superuser'] = False
            user = serializer.save()
            return Response(self.get_serializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login endpoint for staff members"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }
            
            # Include error information in debug mode
            if settings.DEBUG:
                response_data['debug_info'] = {
                    'login_field': request.data.get('login'),
                    'is_authenticated': user.is_authenticated,
                    'is_active': user.is_active,
                    'is_staff_member': user.is_staff_member,
                }
            
            return Response(response_data)
        
        # Include more detailed error information
        error_detail = serializer.errors
        if 'non_field_errors' in error_detail:
            error_detail = error_detail['non_field_errors'][0]
            
        return Response(
            {'detail': str(error_detail)},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False)
    def profile(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class MemberViewSet(viewsets.ModelViewSet):
    """ViewSet for Member operations"""
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter and search members"""
        queryset = Member.objects.all()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(cpf__icontains=search)
            )
        
        return queryset.order_by('name')
