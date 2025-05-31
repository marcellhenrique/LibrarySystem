from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Member


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (staff members)"""
    password = serializers.CharField(write_only=True, min_length=6, required=False)

    class Meta:
        model = User
        fields = ('id', 'login', 'email', 'name', 'role', 'password', 
                 'is_staff_member', 'is_active', 'date_joined')
        read_only_fields = ('id', 'is_active', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """Create a new user with encrypted password"""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update user, handling password separately"""
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):
    """Serializer for user authentication"""
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        login = data.get('login')
        password = data.get('password')

        if not login or not password:
            raise serializers.ValidationError('Both login and password are required.')

        user = authenticate(login=login, password=password)

        if not user or not user.is_active:
            raise serializers.ValidationError('Invalid credentials.')

        if not user.is_staff_member:
            raise serializers.ValidationError('User is not a staff member.')

        data['user'] = user
        return data


class MemberSerializer(serializers.ModelSerializer):
    """Serializer for Member model"""
    class Meta:
        model = Member
        fields = ('id', 'name', 'cpf', 'phone', 'email', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_cpf(self, value):
        """Validate CPF format"""
        cpf = ''.join(filter(str.isdigit, value))
        if len(cpf) != 11:
            raise serializers.ValidationError('CPF must contain exactly 11 digits.')
        return cpf

    def validate_phone(self, value):
        """Validate phone format if provided"""
        if value:
            phone = ''.join(filter(str.isdigit, value))
            if len(phone) < 10 or len(phone) > 15:
                raise serializers.ValidationError('Phone must contain between 10 and 15 digits.')
            return phone
        return value

    def validate_email(self, value):
        """Normalize email address"""
        return value.lower()
