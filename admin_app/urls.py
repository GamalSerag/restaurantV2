from django.urls import path
from .views import AdminDocSubmitView, AdminView

urlpatterns = [
    path('<int:pk>/', AdminView.as_view(), name='admin-details'),
    path('admin-docs/', AdminDocSubmitView.as_view(), name='submit_admin_doc'),
    
]