from rest_framework import viewsets, generics
from .models import Admin
from .serializers import AdminSerializer
from rest_framework.permissions import IsAuthenticated

class AdminView(generics.RetrieveAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAuthenticated]
