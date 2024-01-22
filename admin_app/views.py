from rest_framework import viewsets
from .models import Admin
from .serializers import AdminSerializer
from rest_framework.permissions import IsAuthenticated

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAuthenticated]
