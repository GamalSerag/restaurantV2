from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from admin_app.models import Admin
from auth_app.custom_adapter import CustomSocialAccountAdapter
from customer_app.models import Customer
from payment_app.serializers import SubscriptionSerializer
from restaurant_app.models import Restaurant
from restaurant_app.serializers import RestaurantSerializer
from .models import User
from rest_framework.permissions import AllowAny

from django.contrib.auth import get_user_model

from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.models import SocialToken

from .serializers import CustomSocialLoginSerializer, GoogleSignupSerializer, UserSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from django.views.decorators.csrf import csrf_exempt
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from dj_rest_auth.utils import jwt_encode



logger = logging.getLogger(__name__)

from django.utils import timezone
from django.http import HttpResponse
@csrf_exempt
def current_time_zone(request):
    current_zone = timezone.get_current_timezone_name()
    return HttpResponse(f"Current Time Zone: {current_zone}")

class UserRegistrationView(APIView):

    @transaction.atomic
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
                try:
                    Customer.objects.create(user=user, email=email, phone_number=phone_number, first_name=first_name, last_name=last_name,)
                except Exception as e:
                    return Response({"error": "Bad Customer Data"}, status=status.HTTP_400_BAD_REQUEST)
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
                    try:
                        Admin.objects.create(user=user, phone_number=phone_number, first_name=first_name, last_name=last_name, restaurant=restaurant)
                    except Exception as e:
                        return Response({"error": "Bad Admin Data"}, status=status.HTTP_400_BAD_REQUEST)
                    
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









class UserLoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        serializer = self.serializer_class(data=request.data)
        print(serializer)
        # print(serializer.data)
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        if serializer.is_valid():
            user = serializer.user
            token = serializer.validated_data.get('access')
            
            response_data = {
                # 'token': token,
                'refresh': serializer.validated_data.get('refresh'),
                'username': user.username,
                'role': user.role,
            }

            if user.role == 'restaurant_owner':
                admin_profile = Admin.objects.get(user=user)
                restaurant = admin_profile.restaurant
                subscription_serializer = SubscriptionSerializer(admin_profile.subscription)
                serialized_subscription = subscription_serializer.data

                response_data.update({
                    'restaurant_id': restaurant.id,
                    'restaurant_name': restaurant.name,
                    'subscription': serialized_subscription,
                    'has_submitted_docs': admin_profile.has_submitted_docs,
                    'is_subscribed': admin_profile.is_subscribed,
                    'is_approved': admin_profile.is_approved,
                    'owner_id': admin_profile.id,
                })

            response.data.update(response_data)
            response.set_cookie('auth_token', token, httponly=True, secure=True, samesite='Strict')
        return response

User = get_user_model()






class SocialTokenObtainPairView(SocialLoginView):
    adapter_class = None  # This will be set dynamically based on the social provider

    def get_adapter(self):
        if self.adapter_class is None:
            raise NotImplementedError("SocialTokenObtainPairView requires adapter_class to be set.")
        return self.adapter_class()

    def format_response(self, response):
        refresh = str(response.data.get('refresh'))
        access = str(response.data.get('access'))
        return {'refresh': refresh, 'access': access}

    def get_response(self):
        response = super().get_response()
#         return self.format_response(response)



class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    def format_response(self, response):
        refresh = str(response.data.get('refresh'))
        access = str(response.data.get('access'))
        return {'refresh': refresh, 'access': access}

    def get_response(self):
        response = super().get_response()
        return self.format_response(response)


# class GoogleSignup(APIView):
#     def post(self, request):
#         id_token = request.data.get('credential')

#         google_adapter = GoogleOAuth2Adapter(request)
#         client_class = OAuth2Client
#         user = google_adapter.complete_login(request, app=None, token=id_token, client_class=client_class)

#         if user:
#             # User successfully signed up or logged in
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             })
#         else:
#             return Response({'error': 'Google sign-up failed'}, status=400)
        
GOOGLE_REDIRECT_URL = 'http://localhost:8200'



class GoogleAuthView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = GOOGLE_REDIRECT_URL
    
    # use custom serializer
    # serializer_class = CustomSocialLoginSerializer
    
    # def post(self, request, *args, **kwargs):
    #     # Capture the role from the request data and store it in the session
    #     request.session['temp_role'] = request.data.get('role', 'customer')  # Set a default role as fallback
    #     return super().post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user_role = request.data.get('role', 'customer')
        try:
            response = super().post(request, *args, **kwargs)
            # Get the Google social account linked to the user
            social_account = SocialAccount.objects.get(user=request.user)
            
            User.objects.filter(email=request.user.email).update(role=user_role)
            print("Serializer name:", self.serializer_class.__name__)
            if user_role == 'customer':
                customer_profile, created = Customer.objects.get_or_create(user=request.user )
                customer_profile.email = request.user.email
                customer_profile.first_name = request.user.first_name
                customer_profile.last_name = request.user.last_name
                customer_profile.save()
            elif user_role == 'restaurant_owner':
                admin_profile, created = Admin.objects.get_or_create(user=request.user )
                admin_profile.email = request.user.email
                admin_profile.first_name = request.user.first_name
                admin_profile.last_name = request.user.last_name
                admin_profile.save()

            return response
        except OAuth2Error as e:
            return Response({'error': str(e)}, status=500)



# class GoogleAuthView(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
#     client_class = OAuth2Client
#     callback_url = GOOGLE_REDIRECT_URL
    
#     serializer_class = CustomSocialLoginSerializer

#     def post(self, request, *args, **kwargs):
#         try:
#             response = super().post(request, *args, **kwargs)
#             return response
#         except OAuth2Error as e:
#             return Response({'error': str(e)}, status=500)
# class GoogleRefreshTokenView(APIView):
#     def post(self, request):
#         refresh = request.data.get('refresh')
#         refresh = RefreshToken(refresh)
#         tokens = {
#             'access': str(refresh.access_token),
#             'refresh': str(refresh),
#         }
#         return Response(tokens)



class UserRedirectView(LoginRequiredMixin, RedirectView):
    """
    This view is needed by the dj-rest-auth-library in order to work the google login. It's a bug.
    """

    permanent = False

    def get_redirect_url(self):
        return "redirect-url"

# class CustomLoginView(LoginView):
#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         if response.status_code == status.HTTP_200_OK:
#             refresh = response.data.get('refresh')
#             access = response.data.get('access')
#             response.set_cookie('refresh_token', refresh, httponly=True)
#             response.data['refresh'] = 'hidden'
#         return response
    

    
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out.'})
    
class UserRoleView(APIView):
    authentication_classes = [JWTAuthentication]
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
            return Response({
                                'role': role,
                                'is_subscribed': admin.is_subscribed,
                                'is_approved': admin.is_approved,
                                'is_rejected': admin.is_rejected,
                                'has_submitted_docs': admin.has_submitted_docs,
                                'owner_id': admin.id,
                            }
                            ,status=status.HTTP_200_OK) 
        else :
            return Response({'role': role, 'first_name':first_name, 'last_name': last_name, 'email':email}, status=status.HTTP_200_OK)


        
    
class TestView(APIView):
    def post(self, request):
        print(request.data)

        return Response(request.data)