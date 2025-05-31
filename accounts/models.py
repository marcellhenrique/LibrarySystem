import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator, EmailValidator


class CustomUserManager(BaseUserManager):
    """Custom user model manager with login as the unique identifier"""
    
    def create_user(self, login=None, email=None, password=None, **extra_fields):
        if not login:
            raise ValueError('Login is required')
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        # Set username to login to satisfy AbstractUser requirements
        extra_fields['username'] = login
        user = self.model(login=login, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, login=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff_member', True)
        extra_fields.setdefault('role', 'Administrator')
        return self.create_user(login=login, email=email, password=password, **extra_fields)


class User(AbstractUser):
    """Custom User model for staff members"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=100)
    login = models.CharField(max_length=50, unique=True)
    is_staff_member = models.BooleanField(default=False)
    
    # Override username to use login field for consistency
    username = models.CharField(max_length=50, unique=True)
    
    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['email', 'name', 'role']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Ensure username matches login for consistency
        if self.login:
            self.username = self.login
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.role}"


class Member(models.Model):
    """Model for library members"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    cpf = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='CPF must contain exactly 11 numeric digits'
            )
        ]
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10,15}$',
                message='Phone must contain between 10 and 15 digits'
            )
        ]
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.email}"
