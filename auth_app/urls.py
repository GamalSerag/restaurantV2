from django.urls import path
from auth_app.views import GoogleAuthView, GoogleLogin, TestView, UserRedirectView, UserRegistrationView, UserLoginView, UserLogoutView, UserRoleView, current_time_zone
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', csrf_exempt (UserLoginView.as_view()), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('user-role/', UserRoleView.as_view(), name='user-role'),

    # path('google/login/', GoogleLogin.as_view(), name='google_login'),
    # path('google/signup/', GoogleSignup.as_view(), name='google_signup'),

    # JWT 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('test/', TestView.as_view(), name='TestView'),
    path("google/login/", GoogleAuthView.as_view(), name="google_login"),
    path("google/", GoogleLogin.as_view(), name="google_signup"),
    path("~redirect/", view=UserRedirectView.as_view(), name="redirect"),
    path('current-time-zone/', current_time_zone, name='current_time_zone'),
]


test_url = "https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=http://localhost:8200/&prompt=consent&response_type=code&client_id=711863326926-v943grouifn58ksna3q1v3oir91dlafg.apps.googleusercontent.com&scope=openid%20email%20profile&access_type=offline"