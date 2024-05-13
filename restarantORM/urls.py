from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
# from auth_app.views import SignupView

from restarantORM import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('accounts/', include('allauth.urls')),
    
    path('admin/', admin.site.urls),
    path('api/owner/',include('admin_app.urls')),
    path('api/customer/',include('customer_app.urls')),
    path('api/auth/', include('auth_app.urls')),
    path('api/location/', include('location_app.urls')),
    path('api/restaurants/', include('restaurant_app.urls')),
    path('api/offer/', include('offers_app.urls')),
    path('api/cart/', include('cart_app.urls')),
    path('api/order/', include('order_app.urls')),
    

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('api/rating/', include('review_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)