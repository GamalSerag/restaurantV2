from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Admin, AdminDoc
from .serializers import AdminDocSerializer, AdminSerializer
from rest_framework.permissions import IsAuthenticated
import json

class AdminView(generics.RetrieveAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAuthenticated]




class AdminDocSubmitView(APIView):
    def post(self, request, format=None):
        serializer = AdminDocSerializer(data=request.data)
        if serializer.is_valid():

            admin_id = request.user.admin_profile.id
            serializer.save(admin_id=admin_id)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
