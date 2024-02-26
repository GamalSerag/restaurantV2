from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from admin_app.models import Admin
from customer_app.models import Customer
from payment_app.serializers import SubscriptionSerializer
from restaurant_app.models import Restaurant
from restaurant_app.serializers import RestaurantSerializer
from .models import User

from .serializers import UserSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

logger = logging.getLogger(__name__)

class UserRegistrationView(APIView):
    def post(self, request):
        print(request.data)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():

            user = serializer.save()
            email = request.data.get('email')

            if user.role == 'customer':
                phone_number = request.data.get('phone_number')
                first_name = request.data.get('first_name')
                last_name = request.data.get('last_name')

                user.first_name = first_name
                user.last_name = last_name
                Customer.objects.create(user=user, email=email, phone_number=phone_number, first_name=first_name, last_name=last_name,)
            elif user.role == 'restaurant_owner':

                phone_number = request.data.get('admin_phone_number')
                first_name = request.data.get('first_name')
                last_name = request.data.get('last_name')

                # Extract restaurant details from the request
                restaurant_data = request.data.get('restaurant', {})
                restaurant_data['admin'] = user  # Associate the admin user with the restaurant

                # Create a new restaurant using the extracted data
                restaurant_serializer = RestaurantSerializer(data=restaurant_data)
                if restaurant_serializer.is_valid():
                    restaurant_serializer.save()
                    restaurant = restaurant_serializer.instance
                    Admin.objects.create(user=user, phone_number=phone_number, first_name=first_name, last_name=last_name, restaurant=restaurant)

                    print(f"User registered successfully: {user.username}")
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    # Delete the user if restaurant creation fails
                    user.delete()
                    print(f"Restaurant creation failed. Errors: {restaurant_serializer.errors}")
                    return Response(restaurant_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
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

            # Check if the user is a restaurant owner
            if user.role == 'restaurant_owner':
                # Get the associated Admin profile
                admin_profile = Admin.objects.get(user=user)
                restaurant = admin_profile.restaurant

                subscription_serializer = SubscriptionSerializer(admin_profile.subscription)
                serialized_subscription = subscription_serializer.data

                # Include the restaurant information in the response
                response_data = {
                    'token': token.key,
                    'username': user.username,
                    'role': user.role,
                    
                    'restaurant_id': restaurant.id,
                    'restaurant_name': restaurant.name,  # Include other restaurant details as needed
                    'subscription': serialized_subscription,
                    'is_subscribed': admin_profile.is_subscribed
                }
            else:
                response_data = {
                    'token': token.key,
                    'username': user.username,
                    'role': user.role,
                }

            response = JsonResponse(response_data)
            response.set_cookie('auth_token', token.key, httponly=True, secure=True, samesite='Strict')

            print(f"Login successful: {user.username}")
            return Response(response_data)
        else:
            print(f"Login failed. Invalid email or password.")
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out.'})
    
class UserRoleView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        description="Get the role and additional information of the authenticated user.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "enum": ["customer"]},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "email": {"type": "string"}
                }
            },
            401: {
                "description": "Invalid token",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": { "detail":{ "type": "string" }  },
                            
                            "example": {"detail": "Invalid token"}
                        }
                    }
                }
            }
        },
        parameters=[
            OpenApiParameter(
                name="Authorization",
                location=OpenApiParameter.HEADER,
                required=True,
                description="Token obtained after successful authentication"
            )
        ]
    )

    def get(self, request):
        user = request.user
        role = user.role
        first_name = user.first_name
        last_name = user.last_name
        email = user.email

        # Check if the user is an admin
        if role == 'restaurant_owner':
            admin = user.admin_profile
            is_subscribed = admin.is_subscribed
            return Response({'role': role, 'is_subscribed': is_subscribed}, status=status.HTTP_200_OK)
        elif role == 'customer' :
            return Response({'role': role, 'first_name':first_name, 'last_name': last_name, 'email':email}, status=status.HTTP_200_OK)