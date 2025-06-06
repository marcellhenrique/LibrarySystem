from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class LoginBackend(ModelBackend):
    """Custom authentication backend that uses the 'login' field"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate using login field"""
        UserModel = get_user_model()
        login = username or kwargs.get('login')
        
        if login is None:
            return None
            
        try:
            user = UserModel.objects.get(login=login)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
            
        return None

    def get_user(self, user_id):
        """Get user by ID"""
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
