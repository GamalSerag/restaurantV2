from rest_framework import serializers
from admin_app.models import Admin
from auth_app.serializers import UserSerializer

class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Admin
        fields = '__all__'