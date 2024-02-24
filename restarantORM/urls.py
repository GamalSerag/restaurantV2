from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
# from auth_app.views import SignupView

from restarantORM import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    
    
    path('admin/', admin.site.urls),
    path('api/auth/', include('auth_app.urls')),
    path('api/location/', include('location_app.urls')),
    path('api/restaurants/', include('restaurant_app.urls')),
    path('api/offer/', include('offers_app.urls')),
    

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)