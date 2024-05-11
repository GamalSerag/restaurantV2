from rest_framework import serializers
from .models import User
from rest_framework import serializers
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.serializers import SocialLoginSerializer, SocialConnectSerializer
from django.contrib.auth import get_user_model

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.helpers import complete_social_login

from django.db import transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class GoogleLoginSerializer(SocialLoginSerializer):
    adapter_class = GoogleOAuth2Adapter

class GoogleSignupSerializer(SocialConnectSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email is already in use")
        return email

    def save(self, request):
        adapter = self.get_adapter(request)
        user = adapter.save_user(request, self, email_verified=True)
        return user
    





class CustomSocialLoginSerializer(SocialLoginSerializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='customer')

    @transaction.atomic
    def save(self, request):
        print(f'Request data: {self.validated_data}')
        user = super().save(request)
        print(f'Saved user: {user}')
        user.role = self.validated_data.get('role', 'customer')
        user.save()
        return user