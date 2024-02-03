from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from admin_app.models import Admin
from customer_app.models import Customer
from .models import User

from .serializers import UserSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            email = request.data.get('email')

            if user.role == 'customer':
                Customer.objects.create(user=user, email=email)
            elif user.role == 'restaurant_owner':
                Admin.objects.create(user=user, email=email)
            print(f"User registered successfully: {user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(f"Registration failed. Errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        print(f"Login attempt: email={email}, password={password}")

        # Authenticate using email instead of username
        user = authenticate(request, email=email, password=password)
        print(f"Authenticated user: {user}")

        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            response = JsonResponse({'token': token.key, 'username': user.username, 'role': user.role})
            response.set_cookie('auth_token', token.key, httponly=True, secure=True, samesite='Strict')

            print(f"Login successful: {user.username}")
            return Response({'token': token.key, 'username': user.username, 'role': user.role})
        else:
            print(f"Login failed. Invalid email or password.")
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out.'})