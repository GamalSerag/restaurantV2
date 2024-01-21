from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
# from auth_app.views import SignupView

from restarantORM import settings

urlpatterns = [
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('signup/', SignupView.as_view(), name='signup'),
    # path('admin/', admin.site.urls),
    path('api/location/', include('location_app.urls')),
    path('api/restaurants/', include('restaurant_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)