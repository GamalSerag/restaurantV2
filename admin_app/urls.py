from django.urls import path
from .views import AdminApproveRejectView,  AdminDetailsView, AdminDocSubmitView, AdminDocUpdateView, AdminListView, AdminView

urlpatterns = [
    path('list/', AdminListView.as_view(), name='admins-list'),
    path('<int:pk>/', AdminDetailsView.as_view(), name='admin-details'),
    path('admin-docs/', AdminDocSubmitView.as_view(), name='submit_admin_doc'),
    path('admin-docs/<int:pk>/update/', AdminDocUpdateView.as_view(), name='admin-doc-update'),
    path('approve/<int:pk>/', AdminApproveRejectView.as_view(), name='admin-approve'),
    path('reject/<int:pk>/', AdminApproveRejectView.as_view(), name='admin-reject')
    
]