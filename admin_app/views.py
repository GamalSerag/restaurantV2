from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Admin, AdminDoc
from .serializers import AdminDetailForSuperAdminSerializer, AdminDocSerializer, AdminListSerializer, AdminSerializer
from rest_framework.permissions import IsAuthenticated
import json
from auth_app.permissions import IsAdminOfRestaurant





class AdminListView(generics.ListAPIView):
    # queryset = Admin.objects.all()
    serializer_class = AdminListSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Admin.objects.all()

        # Check if 'submitted_docs' parameter is present in query params and has value 'true'
        submitted_docs_param = self.request.query_params.get('submitted_docs')
        if submitted_docs_param and submitted_docs_param.lower() == 'true':
            queryset = queryset.filter(has_submitted_docs=True)

        # Check if 'approved' parameter is present in query params and has value 'false'
        approved_param = self.request.query_params.get('approved')
        if approved_param and approved_param.lower() == 'false':
            queryset = queryset.filter(is_approved=False)

        # Check if 'rejected' parameter is present in query params and has value 'false'
        rejected_param = self.request.query_params.get('rejected')
        if rejected_param and rejected_param.lower() == 'false':
            queryset = queryset.filter(is_rejected=False)

        return queryset
    

class AdminDetailsView(generics.RetrieveAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminDetailForSuperAdminSerializer
    # permission_classes = [IsAuthenticated]


class AdminView(generics.RetrieveAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAuthenticated]




class AdminDocSubmitView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOfRestaurant]
    def post(self, request, format=None):
        serializer = AdminDocSerializer(data=request.data)
        if serializer.is_valid():
            print(request.data)
            admin = request.user.admin_profile
            admin_id = admin.id
            admin.is_rejected = False
            serializer.save(admin_id=admin_id)
            restaurant = admin.restaurant
            restaurant.latitude = request.data.get('latitude')
            
            restaurant.longitude = request.data.get('longitude')

            restaurant.save()
            admin.save()
            print(restaurant.latitude)
            print(restaurant.longitude)
            
            response_data = serializer.data
            response_data['latitude'] = restaurant.latitude
            response_data['longitude'] = restaurant.longitude
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
    

class AdminDocUpdateView(generics.UpdateAPIView):
    queryset = AdminDoc.objects.all()
    serializer_class = AdminDocSerializer


class AdminApproveRejectView(generics.UpdateAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminListSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        admin_id = self.kwargs.get('pk')
        action = None  # Initialize action variable

        # Check which endpoint was hit based on the URL path
        if 'approve' in request.path:
            action = 'approve'
        elif 'reject' in request.path:
            action = 'reject'
        else:
            return Response({"error": "Invalid endpoint."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            admin = self.queryset.get(id=admin_id)
        except Admin.DoesNotExist:
            return Response({"error": "Admin not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser:
            return Response({"error": "Only superadmins can approve/reject admins."}, status=status.HTTP_403_FORBIDDEN)

        if action == 'approve':
            admin.is_approved = True
            admin.save()
            return Response({"message": "Admin approved successfully."}, status=status.HTTP_200_OK)
        elif action == 'reject':
            admin.is_rejected = True
            if admin.is_approved:  # If previously approved, reset is_approved
                admin.is_approved = False
            admin.save()
            

            # Update superadmin_notes in AdminDoc if rejected
            admin_doc = admin.admin_docs.first()  # Assuming each admin has one AdminDoc
            if admin_doc:
                admin_doc.superadmin_notes = request.data.get('notes', '')
                admin_doc.save()

            serializer = self.serializer_class(admin)
            return Response(serializer.data, status=status.HTTP_200_OK)
    


class SuperadminRejectionNotesView(generics.RetrieveAPIView):
    queryset = AdminDoc.objects.all()
    serializer_class = AdminDocSerializer
