from django.urls import path
from auth_app.views import UserRegistrationView, UserLoginView, UserLogoutView, UserRoleView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('user-role/', UserRoleView.as_view(), name='user-role'),
]