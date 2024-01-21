from rest_framework import generics
from admin_app.models import Admin
from admin_app.serializers import AdminSerializer

class AdminRegistrationView(generics.CreateAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer