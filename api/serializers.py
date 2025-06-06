from rest_framework import serializers
from django.utils import timezone
from .models import Book, Loan, LoanHistory
from accounts.serializers import MemberSerializer


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model"""
    class Meta:
        model = Book
        fields = ('id', 'title', 'category', 'availability', 
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'availability', 'created_at', 'updated_at')

    def to_representation(self, instance):
        """Convert UUIDs to strings for JSON serialization"""
        data = super().to_representation(instance)
        data['id'] = str(instance.id)
        return data

    def validate_title(self, value):
        """Validate and normalize book title"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Title must have at least 2 characters.')
        return value.strip()

    def validate_category(self, value):
        """Validate and normalize book category"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Category must have at least 2 characters.')
        return value.strip()


class LoanSerializer(serializers.ModelSerializer):
    """Serializer for Loan model"""
    member_details = MemberSerializer(source='member', read_only=True)
    book_details = BookSerializer(source='book', read_only=True)

    class Meta:
        model = Loan
        fields = ('id', 'book', 'member', 'loan_date', 'return_date', 
                 'status', 'book_details', 'member_details', 
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'loan_date', 'created_at', 'updated_at')

    def to_representation(self, instance):
        """Convert UUIDs to strings for JSON serialization"""
        data = super().to_representation(instance)
        data['id'] = str(instance.id)
        data['book'] = str(instance.book.id)
        data['member'] = str(instance.member.id)
        return data

    def validate(self, data):
        """Validate loan creation/update"""
        if self.instance is None:  # Creating new loan
            book = data.get('book')
            member = data.get('member')
            
            # Check if member has active loans for this book first
            existing_loan = Loan.objects.filter(
                book=book,
                member=member,
                status='LOANED'
            ).exists()
            if existing_loan:
                raise serializers.ValidationError({
                    'non_field_errors': ['Member already has an active loan for this book.']
                })
            
            # Then check book availability
            if not book.availability:
                raise serializers.ValidationError({
                    'book': 'This book is not available for loan.'
                })

        return data


class LoanReturnSerializer(serializers.ModelSerializer):
    """Serializer for processing book returns"""
    class Meta:
        model = Loan
        fields = ('id', 'return_date', 'status')
        read_only_fields = ('id',)

    def validate(self, data):
        """Validate return operation"""
        if self.instance.status == 'RETURNED':
            raise serializers.ValidationError('This loan has already been returned.')
        
        data['status'] = 'RETURNED'
        data['return_date'] = timezone.now().date()
        return data


class LoanHistorySerializer(serializers.ModelSerializer):
    """Serializer for LoanHistory model"""
    member_details = MemberSerializer(source='member', read_only=True)
    book_details = BookSerializer(source='book', read_only=True)

    class Meta:
        model = LoanHistory
        fields = ('id', 'book', 'member', 'action_date', 'action_type',
                 'book_details', 'member_details', 'created_at')
        read_only_fields = ('id', 'created_at')

    def to_representation(self, instance):
        """Convert UUIDs to strings for JSON serialization"""
        data = super().to_representation(instance)
        data['id'] = str(instance.id)
        data['book'] = str(instance.book.id)
        data['member'] = str(instance.member.id)
        return data
