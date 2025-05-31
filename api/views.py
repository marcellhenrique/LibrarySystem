from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsStaffMember
from django.utils import timezone
from .models import Book, Loan, LoanHistory
from .serializers import (
    BookSerializer, LoanSerializer, LoanReturnSerializer, LoanHistorySerializer
)


class BookViewSet(viewsets.ModelViewSet):
    """ViewSet for Book operations"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsStaffMember]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'category']
    ordering_fields = ['title', 'category', 'created_at']
    ordering = ['title']


class LoanViewSet(viewsets.ModelViewSet):
    """ViewSet for Loan operations"""
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['book__title', 'member__name', 'status']
    ordering_fields = ['loan_date', 'return_date', 'status']
    ordering = ['-loan_date']

    @action(detail=True, methods=['patch'])
    def return_book(self, request, pk=None):
        """Process book return"""
        loan = self.get_object()
        serializer = LoanReturnSerializer(loan, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """Filter loans based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status.upper())
        
        # Filter by member
        member_id = self.request.query_params.get('member', None)
        if member_id:
            queryset = queryset.filter(member_id=member_id)
        
        # Filter by book
        book_id = self.request.query_params.get('book', None)
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        
        return queryset


class LoanHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for LoanHistory (read-only)"""
    queryset = LoanHistory.objects.all()
    serializer_class = LoanHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['book__title', 'member__name']
    ordering_fields = ['action_date', 'created_at']
    ordering = ['-action_date']

    def get_queryset(self):
        """Filter history based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(action_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(action_date__lte=end_date)
        
        # Filter by member
        member_id = self.request.query_params.get('member', None)
        if member_id:
            queryset = queryset.filter(member_id=member_id)
        
        # Filter by book
        book_id = self.request.query_params.get('book', None)
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        
        return queryset
