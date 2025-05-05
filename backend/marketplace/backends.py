from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import MultipleObjectsReturned

User = get_user_model()

class CustomAuthBackend(ModelBackend):
    """
    Custom authentication backend that supports:
    - Email authentication
    - Username authentication
    - Phone number authentication (Namibian format)
    - Case-insensitive email matching
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Try to get by email first (case-insensitive)
        if '@' in username:
            try:
                user = User.objects.get(email__iexact=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                pass
            except MultipleObjectsReturned:
                return None
        
        # Try by username (case-sensitive)
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        
        # Try by phone number (Namibian format)
        if username.startswith('+264'):
            try:
                user = User.objects.get(phone_number=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                pass
        
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None