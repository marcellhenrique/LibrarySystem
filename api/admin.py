from django.contrib import admin
from .models import Book, Loan, LoanHistory


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin configuration for Book model"""
    list_display = ('title', 'category', 'availability', 'created_at')
    list_filter = ('availability', 'category')
    search_fields = ('title', 'category')
    ordering = ('title',)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """Admin configuration for Loan model"""
    list_display = ('book', 'member', 'loan_date', 'return_date', 'status')
    list_filter = ('status', 'loan_date', 'return_date')
    search_fields = ('book__title', 'member__name')
    ordering = ('-loan_date',)
    raw_id_fields = ('book', 'member')


@admin.register(LoanHistory)
class LoanHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for LoanHistory model"""
    list_display = ('book', 'member', 'action_date')
    list_filter = ('action_date',)
    search_fields = ('book__title', 'member__name')
    ordering = ('-action_date',)
    raw_id_fields = ('book', 'member')
