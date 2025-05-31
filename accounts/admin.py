from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Member


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for Staff User model"""
    list_display = ('login', 'email', 'name', 'role', 'is_staff_member', 'is_active')
    list_filter = ('is_staff_member', 'is_active', 'role')
    search_fields = ('login', 'email', 'name')
    ordering = ('login',)
    
    fieldsets = (
        (None, {'fields': ('login', 'email', 'password')}),
        ('Personal info', {'fields': ('name', 'role')}),
        ('Permissions', {'fields': ('is_staff_member', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'email', 'name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """Admin configuration for Member model"""
    list_display = ('name', 'email', 'cpf', 'phone', 'created_at')
    search_fields = ('name', 'email', 'cpf')
    list_filter = ('created_at',)
    ordering = ('name',)
