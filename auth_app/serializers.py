from rest_framework import serializers
from .models import User
from rest_framework import serializers
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.serializers import SocialLoginSerializer, SocialConnectSerializer
from django.contrib.auth import get_user_model


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